# /src/xstate_statemachine/interpreter.py
# -----------------------------------------------------------------------------
# 🚀 Asynchronous Interpreter
# -----------------------------------------------------------------------------
# This module contains the `Interpreter` class, the primary asynchronous state
# machine engine. It inherits from `BaseInterpreter` and implements all the
# necessary `asyncio`-based functionality for event handling, background tasks
# (`after`, `invoke`), and actor management.
#
# This class is the workhorse that brings a machine definition to life in an
# async environment, making it suitable for I/O-bound applications like web
# servers, IoT clients, and automation scripts.
# -----------------------------------------------------------------------------
"""
Provides the primary asynchronous interpreter for running state machines.

The `Interpreter` class manages the state machine's lifecycle in a non-blocking
fashion using Python's `asyncio` library. It processes events from a queue,
handles timed transitions, and invokes asynchronous services, making it the
recommended choice for most modern applications.
"""

# -----------------------------------------------------------------------------
# 📦 Standard Library Imports
# -----------------------------------------------------------------------------
import asyncio
import logging
import uuid
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Union,
    overload,
)

# -----------------------------------------------------------------------------
# 📥 Project-Specific Imports
# -----------------------------------------------------------------------------
from .base_interpreter import BaseInterpreter
from .events import AfterEvent, DoneEvent, Event
from .exceptions import ActorSpawningError, ImplementationMissingError
from .models import (
    ActionDefinition,
    InvokeDefinition,
    MachineNode,
    StateNode,
    TContext,
    TEvent,
)
from .task_manager import TaskManager

# -----------------------------------------------------------------------------
# 🪵 Logger Configuration
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 🚀 Interpreter Class Definition
# -----------------------------------------------------------------------------


class Interpreter(BaseInterpreter[TContext, TEvent]):
    """Brings a state machine to life by interpreting it asynchronously.

    The `Interpreter` is the core runtime engine for the state machine. It
    manages the machine's current state, processes events from an async queue,
    executes actions and side effects, and orchestrates the full state
    transition lifecycle. This includes handling complex asynchronous operations
    like invoked services, timed delays (`after`), and spawned child actors
    (which are themselves `Interpreter` instances).

    It uses a dedicated `TaskManager` to cleanly manage the lifecycle of all
    background `asyncio.Task` objects, ensuring they are properly cancelled
    when states are exited.

    Attributes:
        task_manager (TaskManager): An instance of `TaskManager` that tracks and
            manages all background `asyncio.Task` objects created by this
            interpreter for services and timers.
    """

    def __init__(self, machine: MachineNode[TContext, TEvent]) -> None:
        """Initializes a new asynchronous Interpreter instance.

        Args:
            machine (MachineNode[TContext, TEvent]): The `MachineNode` instance
                that this interpreter will execute.
        """
        # 🏛️ Initialize the base class, passing our own class type so that
        # `from_snapshot` can create the correct `Interpreter` instance.
        super().__init__(machine, interpreter_class=Interpreter)
        logger.info(
            "🚀 Initializing Asynchronous Interpreter for '%s'...", self.id
        )

        # 🗃️ Concurrency & Task Management
        self.task_manager: TaskManager = TaskManager()
        self._event_queue: asyncio.Queue[
            Union[Event, AfterEvent, DoneEvent]
        ] = asyncio.Queue()
        self._event_loop_task: Optional[asyncio.Task[None]] = None

        logger.info("✅ Asynchronous Interpreter '%s' initialized.", self.id)

    # -------------------------------------------------------------------------
    # ⏯️ Public Control API (Start, Stop, Send)
    # -------------------------------------------------------------------------

    async def start(self) -> "Interpreter[TContext, TEvent]":
        """Starts the interpreter and its main event-processing loop.

        This method initializes the machine by transitioning it to its initial
        state and begins the main event loop to process events from the queue.
        It is idempotent; calling `start` on an already running or stopped
        interpreter has no effect and will simply return.

        Returns:
            Interpreter[TContext, TEvent]: The interpreter instance (`self`),
            allowing for convenient method chaining (e.g., `await
            Interpreter(m).start()`).

        Raises:
            Exception: Propagates any exception that occurs during the initial
                state entry, ensuring a clean failure state if the machine
                cannot start correctly.
        """
        # 🛡️ Idempotency check: Don't start if already running or stopped.
        if self.status != "uninitialized":
            logger.warning(
                "⚠️ Interpreter '%s' already running or stopped. Skipping start.",
                self.id,
            )
            return self

        logger.info("🏁 Starting interpreter '%s'...", self.id)
        self.status = "running"
        # 🌀 Launch the main event loop as a background task.
        self._event_loop_task = asyncio.create_task(self._run_event_loop())

        try:
            # 🔔 Notify plugins that the interpreter is starting.
            for plugin in self._plugins:
                plugin.on_interpreter_start(self)

            # 🚀 Enter the initial state(s) of the machine.
            # We use a synthetic init event to allow any entry actions on the
            # root state to execute.
            init_event = Event(type="___xstate_statemachine_init___")
            await self._enter_states([self.machine], init_event)

            logger.info(
                "✅ Interpreter '%s' started successfully. Current states: %s",
                self.id,
                self.current_state_ids,
            )
        except Exception:
            # 💥 If startup fails, perform a graceful shutdown.
            logger.error(
                "💥 Interpreter '%s' failed to start.", self.id, exc_info=True
            )
            self.status = "stopped"
            # Ensure the event loop task is cancelled if it was created.
            if self._event_loop_task and not self._event_loop_task.done():
                self._event_loop_task.cancel()
            raise  # Re-raise the original exception to the caller.

        return self

    async def stop(self) -> None:
        """Stops the interpreter, cleaning up all tasks and spawned actors.

        This method gracefully shuts down the event loop, cancels all running
        background tasks (timers, services), and recursively stops any child
        actors that were spawned by this interpreter. It is idempotent.
        """
        # 🛡️ Idempotency check: Don't stop if not currently running.
        if self.status != "running":
            logger.warning(
                "⚠️ Interpreter '%s' is not running. Skipping stop.", self.id
            )
            return

        logger.info("🛑 Gracefully stopping interpreter '%s'...", self.id)
        self.status = "stopped"

        # 🔔 Notify plugins of the impending shutdown.
        for plugin in self._plugins:
            plugin.on_interpreter_stop(self)

        # 🛑 Stop all child actors recursively.
        for actor in self._actors.values():
            await actor.stop()
        self._actors.clear()

        # ❌ Cancel all background tasks (timers, services) owned by this interpreter.
        await self.task_manager.cancel_all()

        # 🔌 Terminate the main event processing loop.
        if self._event_loop_task:
            self._event_loop_task.cancel()
            # Wait for the loop to acknowledge the cancellation to prevent leaks.
            try:
                await self._event_loop_task
            except asyncio.CancelledError:
                logger.debug(
                    "Event loop task for '%s' acknowledged cancellation.",
                    self.id,
                )
            self._event_loop_task = None

        logger.info("✅ Interpreter '%s' stopped successfully.", self.id)

    @overload
    async def send(self, event_type: str, **payload: Any) -> None: ...  # noqa

    @overload
    async def send(  # noqa
        self, event: Union[Dict[str, Any], Event, DoneEvent, AfterEvent]
    ) -> None: ...

    async def send(
        self,
        event_or_type: Union[
            str, Dict[str, Any], Event, DoneEvent, AfterEvent
        ],
        **payload: Any,
    ) -> None:
        """Sends an event to the machine's internal queue for processing.

        This is the primary method for interacting with a running state machine.
        It provides a flexible API, accepting either a string type with keyword
        arguments for the payload, a dictionary, or a pre-constructed `Event`
        object. This is a non-blocking operation that returns immediately after
        placing the event in the queue.

        Args:
            event_or_type: The event to send. Can be an event type string,
                a dictionary (e.g., `{"type": "MY_EVENT", "value": 42}`),
                or an `Event`, `DoneEvent`, or `AfterEvent` object.
            **payload: Keyword arguments that become the event's payload if
                `event_or_type` is a string.
        """
        # 📦 Use the centralized helper from the base class to normalize the input.
        event_obj = self._prepare_event(event_or_type, **payload)

        # 📥 Place the standardized event object into the async queue.
        await self._event_queue.put(event_obj)

    # -------------------------------------------------------------------------
    # ⚙️ Internal Event Loop & Execution Logic
    # -------------------------------------------------------------------------

    async def _run_event_loop(self) -> None:
        """The main asynchronous event-processing loop for the interpreter."""
        logger.debug("🔄 Event loop started for interpreter '%s'.", self.id)
        try:
            while self.status == "running":
                # 📬 Wait indefinitely for the next event from the queue.
                event = await self._event_queue.get()
                logger.debug(
                    "🔥 Event '%s' dequeued for processing in '%s'.",
                    event.type,
                    self.id,
                )

                # 🔌 Notify plugins that an event is about to be processed.
                for plugin in self._plugins:
                    plugin.on_event_received(self, event)

                # 🧠 Process the event using the core algorithm from BaseInterpreter.
                # This single step will handle the event and any subsequent
                # "always" transitions until the machine is in a stable state.
                await self._process_event_and_transient_transitions(event)

                self._event_queue.task_done()

        except asyncio.CancelledError:
            # This is an expected, clean shutdown triggered by `stop()`.
            logger.debug("🛑 Event loop for '%s' was cancelled.", self.id)
            raise
        except Exception as exc:
            # This indicates a critical, unexpected failure in the machine's logic.
            logger.critical(
                "💥 Fatal error in event loop for '%s': %s",
                self.id,
                exc,
                exc_info=True,
            )
            # Ensure the interpreter is fully stopped on catastrophic failure.
            self.status = "stopped"
            raise
        finally:
            logger.debug("⚓ Event loop for '%s' has exited.", self.id)

    async def _process_event_and_transient_transitions(
        self, event: Union[Event, AfterEvent, DoneEvent]
    ) -> None:
        """Processes a single event and any resulting event-less transitions.

        This method ensures that after an event is processed, the machine
        immediately checks for and takes any available "always" transitions
        until it settles into a stable state. This entire sequence is treated
        as a single, atomic "step".

        Args:
            event: The external event to process first.
        """
        # 1️⃣ Process the initial event that was dequeued.
        await self._process_event(event)

        # 2️⃣ Immediately loop to handle any event-less ("always") transitions.
        #    This continues until no more "always" transitions are available,
        #    at which point the machine state is considered stable.
        while True:
            transient_event = Event(type="")
            transition = self._find_optimal_transition(transient_event)
            if transition and transition.event == "":
                logger.info(
                    "⚡ Processing transient (event-less) transition in '%s'.",
                    self.id,
                )
                await self._process_event(transient_event)
            else:
                break  # No more transient transitions; state is stable.

    async def _execute_actions(
        self, actions: List[ActionDefinition], event: Event
    ) -> None:
        """Asynchronously executes a list of action definitions.

        This implementation respects the asynchronous nature of actions,
        `await`ing them if they are coroutine functions. It also handles the
        special "spawn" action for creating child actors.

        Args:
            actions (List[ActionDefinition]): The list of `ActionDefinition`
                objects to execute.
            event (Event): The event that triggered these actions.

        Raises:
            ImplementationMissingError: If a named action is not defined in the
                machine's logic dictionary.
        """
        if not actions:
            return

        for action_def in actions:
            # 🔔 Notify plugins before executing each action.
            for plugin in self._plugins:
                plugin.on_action_execute(self, action_def)

            # 👶 Handle actor spawning as a special, built-in action type.
            if action_def.type.startswith("spawn_"):
                await self._spawn_actor(action_def, event)
                continue

            # 🔎 Find the implementation for the named action.
            action_callable = self.machine.logic.actions.get(action_def.type)
            if not action_callable:
                raise ImplementationMissingError(
                    f"Action '{action_def.type}' is not implemented."
                )

            # 🏃‍♂️ Execute the action, awaiting if it's an async function.
            if asyncio.iscoroutinefunction(action_callable):
                await action_callable(self, self.context, event, action_def)
            else:
                action_callable(self, self.context, event, action_def)

    # -------------------------------------------------------------------------
    # 🤖 Asynchronous Task Implementations (Actors, Timers, Services)
    # -------------------------------------------------------------------------

    async def _spawn_actor(
        self, action_def: ActionDefinition, event: Event
    ) -> None:
        """Handles the logic for spawning a child state machine actor.

        This method resolves the actor's `MachineNode` from the machine's
        logic, creates a new `Interpreter` instance for it, and starts it as
        a child process managed by the current interpreter.

        Args:
            action_def (ActionDefinition): The `spawn_` action definition.
            event (Event): The event that triggered the spawn action.

        Raises:
            ActorSpawningError: If the source for the actor in the machine's
                `services` logic is not a valid `MachineNode` or an async
                factory function that returns one.
        """
        logger.info("👶 Spawning actor for action: '%s'", action_def.type)
        actor_machine_key = action_def.type.replace("spawn_", "")

        actor_source = self.machine.logic.services.get(actor_machine_key)
        actor_machine: Optional[MachineNode] = None

        # 🏭 The actor source can be a direct machine node or a factory function.
        if isinstance(actor_source, MachineNode):
            actor_machine = actor_source
        elif callable(actor_source):
            # Execute the factory to get the machine definition.
            result = actor_source(self, self.context, event)
            if asyncio.iscoroutine(result):
                result = await result  # Await if the factory is async.
            if isinstance(result, MachineNode):
                actor_machine = result

        if not actor_machine:
            raise ActorSpawningError(
                f"Cannot spawn '{actor_machine_key}'. Source in `services` "
                "is not a valid MachineNode or a function that returns one."
            )

        # 🧬 Create, configure, and start the new child interpreter.
        actor_id = f"{self.id}:{actor_machine_key}:{uuid.uuid4()}"
        child_interpreter = Interpreter(actor_machine)
        child_interpreter.parent = self
        child_interpreter.id = actor_id
        await child_interpreter.start()

        self._actors[actor_id] = child_interpreter
        logger.info(
            "✅ Actor '%s' (child of '%s') spawned and started successfully.",
            actor_id,
            self.id,
        )

    async def _cancel_state_tasks(self, state: StateNode) -> None:
        """Cancels all background tasks associated with an exited state.

        When a state is exited, this method ensures that any running timers
        or invoked services belonging to that state are properly cancelled.
        This prevents orphaned tasks, memory leaks, and race conditions.

        Args:
            state (StateNode): The `StateNode` being exited.
        """
        # Encapsulation: Delegate cancellation to the dedicated TaskManager.
        await self.task_manager.cancel_by_owner(state.id)

    async def _after_timer_task(
        self, delay_sec: float, event: AfterEvent
    ) -> None:
        """Coroutine that waits for a delay and then sends an `AfterEvent`.

        This is the actual task body for a timed transition (`after`).

        Args:
            delay_sec (float): The delay in seconds to wait.
            event (AfterEvent): The `AfterEvent` to send after the delay.
        """
        try:
            await asyncio.sleep(delay_sec)
            logger.info(
                "🕒 'after' timer fired for event '%s' in '%s'.",
                event.type,
                self.id,
            )
            await self.send(event)
        except asyncio.CancelledError:
            # This is expected when a state is exited before the timer fires.
            logger.debug(
                "🚫 'after' timer for event '%s' in '%s' was cancelled.",
                event.type,
                self.id,
            )
            raise  # Re-raise to ensure the task is properly cleaned up.

    def _after_timer(
        self, delay_sec: float, event: AfterEvent, owner_id: str
    ) -> None:
        """Creates and registers a background task for a delayed `AfterEvent`.

        Args:
            delay_sec (float): The delay in seconds.
            event (AfterEvent): The event to be sent after the delay.
            owner_id (str): The ID of the state that owns this timer, used for
                cancellation upon state exit.
        """
        task = asyncio.create_task(self._after_timer_task(delay_sec, event))
        # Register the task with its owner for lifecycle management.
        self.task_manager.add(owner_id, task)

    async def _invoke_service_task(
        self,
        invocation: InvokeDefinition,
        service: Callable[..., Awaitable[Any]],
    ) -> None:
        """Wrapper coroutine that runs an invoked service and handles its result.

        This coroutine manages the full lifecycle of a service invocation: it
        runs the service, captures its successful result or any exceptions, and
        sends the appropriate `DoneEvent` (`done.invoke.*` or `error.platform.*`)
        back to the machine's event queue.

        Args:
            invocation (InvokeDefinition): The metadata for the service invocation.
            service (Callable[..., Awaitable[Any]]): The actual async callable
                service implementation from the machine's logic.
        """
        logger.info(
            "📞 Invoking service '%s' (ID: '%s')...",
            invocation.src,
            invocation.id,
        )
        for plugin in self._plugins:
            plugin.on_service_start(self, invocation)

        try:
            # Create a synthetic event to pass to the service if it needs context.
            invoke_event = Event(
                type=f"invoke.{invocation.id}",
                payload={"input": invocation.input or {}},
            )
            # 🏃‍♂️ Await the actual service coroutine.
            result = await service(self, self.context, invoke_event)

            # ✅ Service completed, send a 'done' event with the result data.
            done_event = DoneEvent(
                type=f"done.invoke.{invocation.id}",
                data=result,
                src=invocation.id,
            )
            await self.send(done_event)
            logger.info(
                "✅ Service '%s' (ID: '%s') completed successfully.",
                invocation.src,
                invocation.id,
            )
            for plugin in self._plugins:
                plugin.on_service_done(self, invocation, result)

        except asyncio.CancelledError:
            # 🚫 Service was cancelled (due to state exit). This is a clean path.
            logger.debug(
                "🚫 Service '%s' (ID: '%s') was cancelled.",
                invocation.src,
                invocation.id,
            )
            raise  # Re-raise to ensure the task is marked as cancelled.

        except Exception as e:
            # 💥 Service raised an unhandled exception.
            logger.error(
                "💥 Service '%s' (ID: '%s') failed: %s",
                invocation.src,
                invocation.id,
                e,
                exc_info=True,
            )
            # Send an 'error' event so the machine can transition to a failure state.
            error_event = DoneEvent(
                type=f"error.platform.{invocation.id}",
                data=e,
                src=invocation.id,
            )
            await self.send(error_event)
            for plugin in self._plugins:
                plugin.on_service_error(self, invocation, e)

    def _invoke_service(
        self,
        invocation: InvokeDefinition,
        service: Callable[..., Any],
        owner_id: str,
    ) -> None:
        """Creates and registers a background task to run an invoked service or actor.

        This method acts as a dispatcher.
        - If the service is a `MachineNode`, it's spawned as a child actor.
        - If the service is a `Callable`, it's run as a standard async task.

        Args:
            invocation: The invoke definition from the state config.
            service: The service implementation or MachineNode from logic.
            owner_id: The ID of the state that owns this invocation.
        """
        # 🎭 Case 1: The service is a MachineNode, so we spawn it as an actor.
        if isinstance(service, MachineNode):
            # Create a task to manage the actor's lifecycle and handle onDone/onError.
            task = asyncio.create_task(
                self._spawn_and_manage_actor(invocation, service)
            )
            self.task_manager.add(owner_id, task)
            return

        # 📞 Case 2: The service is a standard callable.
        async def _invoke_wrapper() -> None:
            # This sleep(0) is a critical best practice to prevent a race
            # condition, ensuring the task is registered before the service
            # code runs.
            await asyncio.sleep(0)
            await self._invoke_service_task(invocation, service)

        task = asyncio.create_task(_invoke_wrapper())
        # Register the task with its owner for lifecycle management.
        self.task_manager.add(owner_id, task)

    async def _spawn_and_manage_actor(
        self, invocation: InvokeDefinition, actor_machine: MachineNode
    ) -> None:
        """Spawns, starts, and manages an actor, sending events on completion.

        This coroutine wraps the entire lifecycle of a child actor that was
        created via `invoke`. It waits for the child to finish and then sends
        the appropriate `onDone` or `onError` event to the parent.

        Args:
            invocation: The invoke definition containing the actor's config.
            actor_machine: The MachineNode definition for the actor.
        """
        child_interpreter = None
        try:
            # 🧬 Create, configure, and start the new child interpreter.
            actor_id = f"{self.id}:{invocation.src}:{uuid.uuid4()}"
            child_interpreter = Interpreter(actor_machine)
            child_interpreter.parent = self
            child_interpreter.id = actor_id
            self._actors[actor_id] = child_interpreter

            for plugin in self._plugins:
                plugin.on_service_start(self, invocation)
            logger.info(
                "🚀 Actor '%s' (ID: %s) invoked by '%s'...",
                invocation.src,
                actor_id,
                self.id,
            )
            # This will run the child interpreter's event loop until it stops.
            await child_interpreter.start()

            # ✅ Child finished cleanly (reached a top-level final state).
            done_event = DoneEvent(
                type=f"done.invoke.{invocation.id}",
                data=child_interpreter.context,  # Return child's final context
                src=invocation.id,
            )
            await self.send(done_event)
            for plugin in self._plugins:
                plugin.on_service_done(self, invocation, done_event.data)

        except asyncio.CancelledError:
            # 🚫 Parent state was exited, cleanly cancel the actor.
            logger.debug(
                "🚫 Actor '%s' (ID: %s) was cancelled.",
                invocation.src,
                invocation.id,
            )
            if child_interpreter:
                await child_interpreter.stop()
            raise

        except Exception as e:
            # 💥 Child actor failed with an unhandled exception.
            logger.error(
                "💥 Actor '%s' (ID: '%s') failed: %s",
                invocation.src,
                invocation.id,
                e,
                exc_info=True,
            )
            error_event = DoneEvent(
                type=f"error.platform.{invocation.id}",
                data=e,
                src=invocation.id,
            )
            await self.send(error_event)
            for plugin in self._plugins:
                plugin.on_service_error(self, invocation, e)
        finally:
            if child_interpreter and child_interpreter.id in self._actors:
                del self._actors[child_interpreter.id]
