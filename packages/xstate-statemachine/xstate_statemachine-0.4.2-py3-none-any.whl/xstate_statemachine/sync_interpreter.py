# /src/xstate_statemachine/sync_interpreter.py
# -----------------------------------------------------------------------------
# ⛓️ Synchronous State Machine Interpreter
# -----------------------------------------------------------------------------
# This module provides the `SyncInterpreter`, a fully synchronous engine for
# executing state machines. It inherits from `BaseInterpreter` and implements
# a blocking, sequential event processing model.
#
# This interpreter is designed for use cases where asynchronous programming is
# not necessary or desired, such as in command-line tools, desktop GUI
# event loops, or for simpler, predictable testing scenarios.
#
# It adheres to the "Template Method" pattern by overriding the abstract async
# methods from `BaseInterpreter` with concrete synchronous implementations,
# while intentionally raising `NotSupportedError` for features that are

# -----------------------------------------------------------------------------
# 📦 Standard Library Imports
# -----------------------------------------------------------------------------
import logging
import threading
import time
import uuid
from collections import deque
from typing import (
    Any,
    Callable,
    Deque,
    Dict,
    List,
    Optional,
    Set,
    Union,
    overload,
)

# -----------------------------------------------------------------------------
# 📥 Project-Specific Imports
# -----------------------------------------------------------------------------
from .base_interpreter import BaseInterpreter
from .events import AfterEvent, DoneEvent, Event
from .exceptions import (
    ActorSpawningError,
    ImplementationMissingError,
    NotSupportedError,
    StateNotFoundError,
)
from .models import (
    ActionDefinition,
    InvokeDefinition,
    MachineNode,
    StateNode,
    TContext,
    TEvent,
    TransitionDefinition,
)
from .resolver import resolve_target_state

# -----------------------------------------------------------------------------
# 🪵 Logger Configuration
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# ⛓️ SyncInterpreter Class Definition
# -----------------------------------------------------------------------------
class SyncInterpreter(BaseInterpreter[TContext, TEvent]):
    """Brings a state machine definition to life by interpreting its behavior synchronously.

    The `SyncInterpreter` manages the machine's state and processes events
    sequentially and immediately within the `send` method call. It is suitable
    for simpler, blocking workflows where asynchronous operations are not needed.

    **Key Characteristics**:
    - **Blocking Execution**: The `send` method blocks until the current event
      and all resulting transitions (including transient "always" transitions)
      are fully processed.
    - **Sequential Processing**: Events are handled one at a time from an
      internal queue, ensuring a predictable order of operations.

    **Design Pattern**:
    This class is a concrete implementation of the "Template Method" pattern
    defined in `BaseInterpreter`. It provides synchronous versions of abstract
    methods related to action execution and service invocation.

    Attributes:
        _event_queue (Deque[Union[Event, AfterEvent, DoneEvent]]): A queue to
            manage the event processing sequence in a first-in, first-out (FIFO) manner.
        _is_processing (bool): A flag to prevent re-entrant event processing,
            ensuring atomicity of a single `send` call's execution loop.
        _after_threads (Dict[str, threading.Thread]): Tracks background threads for `after` timers.
        _after_events (Dict[str, threading.Event]): Manages cancellation signals for `after` timers.
    """

    # -------------------------------------------------------------------------
    # 🧙 Magic Methods & Initialization
    # -------------------------------------------------------------------------

    def __init__(self, machine: MachineNode[TContext, TEvent]) -> None:
        """Initializes a new synchronous Interpreter instance.

        Args:
            machine: The state machine definition that this interpreter will run.
        """
        # 🤝 Initialize the base interpreter first
        super().__init__(machine, interpreter_class=SyncInterpreter)
        logger.info("⛓️ Initializing Synchronous Interpreter... 🚀")

        # ⚙️ Initialize synchronous-specific attributes
        self._event_queue: Deque[Union[Event, DoneEvent, AfterEvent]] = deque()
        self._is_processing: bool = False
        self._after_threads: Dict[str, threading.Thread] = {}
        self._after_events: Dict[str, threading.Event] = {}

        logger.info("✅ Synchronous Interpreter '%s' initialized. 🎉", self.id)

    # -------------------------------------------------------------------------
    # 🌐 Public API
    # -------------------------------------------------------------------------

    def start(self) -> "SyncInterpreter":
        """Starts the interpreter and transitions it to its initial state.

        This method is idempotent; calling `start` on an already running or
        stopped interpreter has no effect. Unlike asynchronous interpreters,
        this does not start a background event loop but simply sets the machine
        to its entry state and processes any immediate "always" transitions.

        Returns:
            The interpreter instance itself, allowing for method chaining.

        Example:
            >>> machine = create_machine(...) # noqa
            >>> interpreter = SyncInterpreter(machine).start()
            >>> print(interpreter.status)
            'running'
        """
        # 🚦 Idempotency check: only start if uninitialized.
        if self.status != "uninitialized":
            logger.info(
                "🚧 Interpreter '%s' already running or stopped. Skipping start.",
                self.id,
            )
            return self

        logger.info("🏁 Starting sync interpreter '%s'...", self.id)
        self.status = "running"

        # ✅ Define a pseudo-transition for the initial state entry
        initial_transition = TransitionDefinition(
            event="___xstate_statemachine_init___",
            config={},
            source=self.machine,
        )

        # 🔌 Notify plugins about the interpreter start and initial transition
        for plugin in self._plugins:
            plugin.on_interpreter_start(self)
            # Pass an empty set as `from_states` for the initial transition
            plugin.on_transition(
                self, set(), self._active_state_nodes, initial_transition
            )

        # ➡️ Enter the machine's initial states.
        self._enter_states([self.machine])
        # 🔄 Process any immediate "always" transitions upon startup.
        self._process_transient_transitions()

        logger.info(
            "✨ Sync interpreter '%s' started. Current states: %s",
            self.id,
            self.current_state_ids,
        )
        return self

    def stop(self) -> None:
        """Stops the interpreter and cleans up all associated resources.

        This method stops all child actors, cancels any pending `after` timers,
        and sets the interpreter's status to 'stopped', preventing further
        event processing. It's idempotent.
        """
        # 🚦 Idempotency check
        if self.status != "running":
            return

        logger.info(
            "🛑 Stopping sync interpreter '%s' and its actors…", self.id
        )

        # 1️⃣ Stop every child actor (blocking & non-blocking)
        for actor_id, actor in list(self._actors.items()):
            try:
                actor.stop()
            finally:
                self._actors.pop(actor_id, None)

        # 2️⃣ Cancel all `after` timers by signaling their cancellation events
        for state_id in list(self._after_events.keys()):
            self._after_events[state_id].set()
        self._after_events.clear()
        self._after_threads.clear()

        # 3️⃣ Update status to prevent further operations
        self.status = "stopped"

        # 4️⃣ Notify plugins about the stop event
        for plugin in self._plugins:
            plugin.on_interpreter_stop(self)

        logger.info("🕊️ Sync interpreter '%s' stopped successfully.", self.id)

    @overload
    def send(self, event_type: str, **payload: Any) -> None: ...  # noqa: E704

    @overload
    def send(  # noqa: PyMethodOverriding
        self, event: Union[Dict[str, Any], Event, DoneEvent, AfterEvent]
    ) -> None:  # noqa
        ...

    def send(
        self,
        event_or_type: Union[
            str, Dict[str, Any], Event, DoneEvent, AfterEvent
        ],
        **payload: Any,
    ) -> None:
        """Sends an event to the machine for immediate, synchronous processing.

        Events are queued and processed sequentially. If an event is sent while
        the interpreter is already processing another, it's added to the queue
        and handled once the current processing cycle completes. This method
        blocks until the sent event and any resulting transient transitions
        are fully resolved.

        Args:
            event_or_type: The event to send. This can be:
                - A `str`: The type of the event, with `payload` as kwargs.
                - A `dict`: An event object, which must contain a 'type' key.
                - An `Event`, `DoneEvent`, or `AfterEvent` instance.
            **payload: Additional keyword arguments for the event's payload,
                used only when `event_or_type` is a string.

        Raises:
            TypeError: If an unsupported event type is passed.
        """
        # 🚦 Halt if the interpreter is not in a 'running' state.
        if self.status != "running":
            logger.warning("🚫 Cannot send event. Interpreter is not running.")
            return

        # 📦 Normalize the input into a standardized Event object.
        event_obj: Union[Event, DoneEvent, AfterEvent]
        if isinstance(event_or_type, str):
            event_obj = Event(type=event_or_type, payload=payload)
        elif isinstance(event_or_type, dict):
            local_payload = event_or_type.copy()
            event_type = local_payload.pop("type", "UnnamedEvent")
            event_obj = Event(type=event_type, payload=local_payload)
        elif isinstance(event_or_type, (Event, DoneEvent, AfterEvent)):
            event_obj = event_or_type
        else:
            # ❌ Raise an error for unsupported event types.
            raise TypeError(
                f"Unsupported event type passed to send(): {type(event_or_type)}"
            )

        # 📥 Add the normalized event to the processing queue.
        self._event_queue.append(event_obj)

        # 🔒 If already processing, the event is queued and will be handled
        #    by the existing processing loop. This prevents re-entrant execution.
        if self._is_processing:
            logger.debug(
                "🔄 Interpreter already processing. Event '%s' queued.",
                event_obj.type,
            )
            return

        # 🎬 Start the main event processing loop.
        self._is_processing = True
        try:
            # 🔁 Process events from the queue until it's empty.
            while self._event_queue:
                current_event = self._event_queue.popleft()
                logger.info("⚙️ Processing event: '%s'", current_event.type)

                # 🔌 Notify plugins that an event is being processed.
                for plugin in self._plugins:
                    plugin.on_event_received(self, current_event)

                # 🎯 Find and execute the transition for the current event.
                self._process_event(current_event)
                # 🔄 Check for any resulting event-less ("always") transitions.
                self._process_transient_transitions()
        finally:
            # 🔓 Reset the processing flag, allowing new `send` calls to start the loop.
            self._is_processing = False
            logger.debug("🎉 Event processing cycle completed. Queue empty.")

    # -------------------------------------------------------------------------
    # ⚙️ Core State Transition Logic (Private)
    # -------------------------------------------------------------------------

    def _process_event(
        self, event: Union[Event, DoneEvent, AfterEvent]
    ) -> None:
        """Finds and executes the optimal transition for a given event.

        This method acts as the entry point for processing a single event,
        finding the appropriate transition, and delegating to the processing helper.

        Args:
            event: The event object to process.
        """
        # 1. Select the winning transition based on event, guards, and state depth.
        transition = self._find_optimal_transition(event)
        if not transition:
            logger.debug(
                "🤷 No valid transition found for event '%s'.", event.type
            )
            return

        # 2. A "targetless" transition only executes actions without changing state.
        if not transition.target_str:
            logger.info("🔄 Executing internal transition actions.")
            self._execute_actions(transition.actions, event)
            for plugin in self._plugins:
                plugin.on_transition(
                    self,
                    self._active_state_nodes,
                    self._active_state_nodes,
                    transition,
                )
            return

        # 3. Resolve the target state node.
        target_state = self._resolve_target_state_robustly(transition)

        # 4. A self-transition without `reenter: True` is also internal.
        if target_state == transition.source and not transition.reenter:
            logger.info("🔄 Executing internal transition actions.")
            self._execute_actions(transition.actions, event)
            for plugin in self._plugins:
                plugin.on_transition(
                    self,
                    self._active_state_nodes,
                    self._active_state_nodes,
                    transition,
                )
            return

        # 5. All other transitions are external; process the state change.
        self._process_single_transition(transition, event, target_state)

    def _process_single_transition(
        self,
        transition: TransitionDefinition,
        event: Event,
        target_state: StateNode,
    ) -> None:
        """Processes a single, specific external transition.

        Args:
            transition: The external `TransitionDefinition` to execute.
            event: The event that triggered this transition.
            target_state: The pre-resolved target `StateNode`.
        """
        # For external transitions, prepare for state changes.
        snapshot_before_transition = self._active_state_nodes.copy()
        domain = self._find_transition_domain(transition, target_state)

        # Determine the full path of states to exit and enter.
        path_to_enter = self._get_path_to_state(target_state, stop_at=domain)
        states_to_exit: Set[StateNode] = {
            s
            for s in self._active_state_nodes
            if self._is_descendant(s, domain) and s is not domain
        }

        # Execute the transition sequence (Exit -> Actions -> Enter)
        self._exit_states(
            sorted(
                list(states_to_exit), key=lambda s: len(s.id), reverse=True
            ),
            event,
        )
        self._execute_actions(transition.actions, event)
        self._enter_states(path_to_enter, event)

        # Finalize the state change and notify plugins.
        self._active_state_nodes.difference_update(states_to_exit)
        self._active_state_nodes.update(path_to_enter)
        for plugin in self._plugins:
            plugin.on_transition(
                self,
                snapshot_before_transition,
                self._active_state_nodes.copy(),
                transition,
            )

    def _process_transient_transitions(self) -> None:
        """Continuously processes event-less ("always") transitions until stable.

        These transitions are checked after any state change. They allow for
        conditional, immediate jumps without an external event. The loop

        continues until no more "always" transitions are available and the
        state configuration is stable.
        """
        logger.debug("🔍 Checking for transient ('always') transitions...")
        while True:
            # 👻 Use a dummy event for guard evaluation in "always" transitions.
            transient_event = Event(type="")  # Empty type signifies "always".

            # 🎯 Find the most specific transient transition available.
            transition = self._find_optimal_transition(transient_event)

            # ⚡ An event-less transition is one with an empty event string ("").
            if transition and transition.event == "":
                logger.info(
                    "🚀 Processing transient transition from '%s' to target '%s'",
                    transition.source.id,
                    transition.target_str or "self (internal)",
                )
                # 🔄 Directly process the *found* transition, which is more efficient.
                self._process_event(transient_event)
            else:
                # ✅ No more transient transitions found. The state is stable.
                logger.debug(
                    "🧘 State is stable. No more transient transitions."
                )
                break

    # -------------------------------------------------------------------------
    # ➡️⬅️ State Lifecycle Hooks (Private)
    # -------------------------------------------------------------------------

    def _enter_states(
        self, states_to_enter: List[StateNode], event: Optional[Event] = None
    ) -> None:
        """Synchronously enters a list of states and executes their entry logic.

        This method handles adding states to the active set, executing 'on_entry'
        actions, invoking services, scheduling timers, and recursively entering
        initial states for compound/parallel states.

        Args:
            states_to_enter: A list of `StateNode` objects to enter,
                ordered from parent to child.
            event: The optional event that triggered the state entry.
        """
        for state in states_to_enter:
            logger.info("➡️ Entering state: '%s'", state.id)
            self._active_state_nodes.add(state)
            self._execute_actions(state.entry, Event(f"entry.{state.id}"))

            # 🏁 Handle final state logic by firing a `done` event if applicable.
            if state.type == "final":
                logger.debug(
                    "🏁 Final state '%s' entered. Checking parent for 'on_done'.",
                    state.id,
                )
                self._check_and_fire_on_done(state)

            # 🌳 For compound states, recursively enter their initial child state.
            if state.type == "compound" and state.initial:
                initial_child = state.states.get(state.initial)
                if initial_child:
                    logger.debug(
                        "🌲 Entering initial child '%s' for compound state '%s'.",
                        initial_child.id,
                        state.id,
                    )
                    self._enter_states([initial_child])
                else:
                    logger.error(
                        "🐛 Initial state '%s' not found for compound state '%s'.",
                        state.initial,
                        state.id,
                    )

            # 🌐 For parallel states, recursively enter all child regions.
            elif state.type == "parallel":
                logger.debug(
                    "🌐 Entering all regions for parallel state '%s'.",
                    state.id,
                )
                self._enter_states(list(state.states.values()))

            # ⚙️ Schedule any tasks (invokes, timers).
            self._schedule_state_tasks(state)
            logger.debug("✅ State '%s' entered successfully.", state.id)

    def _exit_states(
        self, states_to_exit: List[StateNode], event: Optional[Event] = None
    ) -> None:
        """Synchronously exits a list of states and executes their exit logic.

        This handles canceling any tasks associated with the state, executing
        'on_exit' actions, and removing states from the active set.

        Args:
            states_to_exit: A list of `StateNode` objects to exit,
                ordered from child to parent.
            event: The optional event that triggered the state exit.
        """
        # 🧹 Cancel tasks BEFORE any other processing to prevent race conditions.
        for state in states_to_exit:
            self._cancel_state_tasks(state)

        # 🏃‍♂️ Then proceed with normal exit processing.
        for state in states_to_exit:
            logger.info("⬅️ Exiting state: '%s'", state.id)
            self._execute_actions(state.exit, Event(f"exit.{state.id}"))
            self._active_state_nodes.discard(state)
            logger.debug("✅ State '%s' exited successfully.", state.id)

    def _check_and_fire_on_done(self, final_state: StateNode) -> None:
        """Checks if an ancestor state is "done" and queues a `done.state.*` event.

        Triggered when a final state is entered. It checks if the parent
        state has met its completion criteria (e.g., all parallel regions
        are in final states). If so, it queues the corresponding `on_done` event.

        Args:
            final_state: The final state that was just entered.
        """
        ancestor = final_state.parent
        logger.debug(
            "🔍 Checking 'done' status for ancestors of final state '%s'.",
            final_state.id,
        )
        while ancestor:
            # 🧐 Check if the ancestor has an `on_done` handler and is fully completed.
            if ancestor.on_done and self._is_state_done(ancestor):
                done_event_type = f"done.state.{ancestor.id}"
                logger.info(
                    "🥳 State '%s' is done! Queuing onDone event: '%s'",
                    ancestor.id,
                    done_event_type,
                )
                # 📬 Send the `done.state.*` event for the next processing cycle.
                self.send(Event(type=done_event_type))
                return  # 🛑 Only fire the event for the nearest completed ancestor.

            ancestor = ancestor.parent

    # -------------------------------------------------------------------------
    # ⚡ Action & Service Execution (Private Overrides)
    # -------------------------------------------------------------------------

    def _execute_actions(
        self, actions: List[ActionDefinition], event: Event
    ) -> None:
        """Synchronously executes a list of actions.

        This method iterates through action definitions, validates them, and
        executes the corresponding implementation from the machine's logic.
        It specifically handles spawning actors and raises errors for async actions.

        Args:
            actions: The list of `ActionDefinition` objects to execute.
            event: The event that triggered these actions.

        Raises:
            ImplementationMissingError: If an action implementation is not found.
            NotSupportedError: If an async action is encountered.
        """
        if not actions:
            return

        for action_def in actions:
            # 🔌 Notify plugins before execution
            for plugin in self._plugins:
                plugin.on_action_execute(self, action_def)

            # 🎭 Handle actor spawning actions
            if action_def.type.startswith(("spawn_", "spawn_blocking_")):
                self._spawn_actor(action_def, event)
                continue

            # ⚙️ Handle normal actions
            action_impl = self.machine.logic.actions.get(action_def.type)
            if not action_impl:
                raise ImplementationMissingError(
                    f"Action '{action_def.type}' not implemented."
                )
            # 🚫 Reject async actions
            if self._is_async_callable(action_impl):
                raise NotSupportedError(
                    f"Async action '{action_def.type}' not supported by SyncInterpreter."
                )
            # ▶️ Execute the synchronous action
            action_impl(self, self.context, event, action_def)

    def _spawn_actor(self, action_def: ActionDefinition, event: Event) -> None:
        """Spawns a child state machine actor in blocking or non-blocking mode.

        Args:
            action_def: The action definition for spawning the actor.
            event: The event that triggered the spawn action.

        Raises:
            ActorSpawningError: If the specified service is not a valid
                `MachineNode` or a factory that returns one.
        """
        # 🕵️ Determine mode (blocking vs. non-blocking) and service key
        blocking = action_def.type.startswith("spawn_blocking_")
        key = action_def.type.split("_", 2)[-1]
        logger.info("🎭 Spawning actor '%s' (Blocking: %s)", key, blocking)

        # 🏭 Get the actor's machine definition from the services registry
        source = self.machine.logic.services.get(key)
        actor_machine = (
            source
            if isinstance(source, MachineNode)
            else (
                source(self, self.context, event) if callable(source) else None
            )
        )
        if not isinstance(actor_machine, MachineNode):
            raise ActorSpawningError(
                f"Cannot spawn '{key}'. Service not a MachineNode or factory."
            )

        # 🆔 Create and register the child interpreter (actor)
        actor_id = f"{self.id}:{key}:{uuid.uuid4()}"
        child = SyncInterpreter(actor_machine)
        child.parent = self
        child.id = actor_id
        self._actors[actor_id] = child

        # --- Blocking Execution Path ---
        if blocking:
            child.start()
            return

        # --- Non-Blocking Execution Path (via a background thread) ---
        def _runner() -> None:
            """Starts the child and cleans up when it's done or stopped."""
            try:
                # 🚀 Start the actor in the background thread.
                child.start()
                # 🔄 Keep the thread alive while the child runs.
                while child.status == "running":
                    # 🏁 Exit loop if the child reaches a top-level final state.
                    if any(
                        s.is_final and s.parent == child.machine
                        for s in child._active_state_nodes
                    ):
                        break
                    time.sleep(0.01)  # 🤏 Yield to prevent busy-waiting.
            finally:
                # 🧹 Ensure cleanup happens whether the child finishes or is stopped.
                child.stop()
                self._actors.pop(actor_id, None)
                logger.info("🧹 Actor thread for '%s' cleaned up.", actor_id)

        # 🚀 Start the thread
        threading.Thread(
            target=_runner, daemon=True, name=f"actor-{actor_id}"
        ).start()

    def _cancel_state_tasks(self, state: StateNode) -> None:
        """Cancel all pending **after** timers that belong to a state.

        This handles *multiple* timers per state by matching a prefix-based key.
        Older code assumed one timer per state and leaked others.

        Args:
            state (StateNode): The state whose timers should be cancelled.
        """
        state_prefix = f"{state.id}::"  # our internal key scheme
        to_cancel = [
            k
            for k in list(self._after_events.keys())
            if k == state.id or k.startswith(state_prefix)
        ]

        if not to_cancel:
            logger.debug(
                "🧹 No 'after' timers to cancel for state '%s'.", state.id
            )
            return

        for key in to_cancel:
            try:
                logger.debug(
                    "🧹 Cancelling 'after' timer key='%s' (owner='%s')",
                    key,
                    state.id,
                )
                self._after_events[key].set()  # signal cancellation
            finally:
                # Remove from tracking dicts whether the thread is alive or not;
                # the thread cleans itself up on exit as well.
                self._after_events.pop(key, None)
                self._after_threads.pop(key, None)

    def _after_timer(
        self, delay_sec: float, event: AfterEvent, owner_id: str
    ) -> None:
        """Schedule a delayed `AfterEvent` on a background thread.

        Supports **multiple timers per owner** by storing them under unique keys.
        Threads watch a cancellation `Event` so exits cleanly on state leave.

        Args:
            delay_sec (float): Delay (seconds) before firing.
            event (AfterEvent): Event to send when the timer expires.
            owner_id (str): ID of the state that owns this timer.
        """
        # Generate a unique handle so a state can own several timers simultaneously.
        unique_key = f"{owner_id}::{uuid.uuid4()}"
        cancel_event = threading.Event()

        logger.info(
            "⏰ Scheduling 'after' (%s) in %.2fs for state '%s' [key=%s]",
            event.type,
            delay_sec,
            owner_id,
            unique_key,
        )

        # Register for lifecycle management.
        self._after_events[unique_key] = cancel_event

        def timer_thread() -> None:
            """Worker that waits, checks cancellation, and sends the event."""
            try:
                cancelled = cancel_event.wait(timeout=delay_sec)
                if cancelled:
                    logger.debug(
                        "🚫 Timer cancelled before firing [key=%s].",
                        unique_key,
                    )
                    return

                # Fire only if interpreter still running AND owner still active.
                if self.status == "running" and any(
                    s.id == owner_id for s in self._active_state_nodes
                ):
                    logger.debug(
                        "🕒 Timer expired -> sending event '%s' [key=%s].",
                        event.type,
                        unique_key,
                    )
                    self.send(event)
                else:
                    logger.debug(
                        "⚠️ Timer expired but owner inactive or interpreter stopped [key=%s].",
                        unique_key,
                    )
            except Exception as exc:  # pragma: no cover (safety net)
                logger.error(
                    "💥 Error in after-timer thread [key=%s]: %s",
                    unique_key,
                    exc,
                    exc_info=True,
                )
            finally:
                # Ensure we don't leak references.
                self._after_threads.pop(unique_key, None)
                self._after_events.pop(unique_key, None)

        thread = threading.Thread(
            target=timer_thread, daemon=True, name=f"after-{unique_key}"
        )
        self._after_threads[unique_key] = thread
        thread.start()

    def _invoke_service(
        self,
        invocation: InvokeDefinition,
        service: Callable[..., Any],
        owner_id: str,
    ) -> None:
        """Handles invoked services, supporting only synchronous callables.

        Synchronous services are executed immediately, blocking the interpreter.
        The service's return value is sent as a `done.invoke.*` event. If it
        raises an exception, an `error.platform.*` event is sent instead.

        Args:
            invocation: The definition of the invoked service.
            service: The callable representing the service logic.
            owner_id: The ID of the state node owns this invocation.

        Raises:
            NotSupportedError: If the provided service is an `async def` function.
        """
        # 🧐 Validate that the service is not an async function.
        if self._is_async_callable(service):
            logger.error(
                "🚫 Service '%s' is async and not supported by SyncInterpreter.",
                invocation.src,
            )
            raise NotSupportedError(
                f"Service '{invocation.src}' is async and not supported."
            )

        logger.info(
            "📞 Invoking sync service '%s' (id: '%s')...",
            invocation.src,
            invocation.id,
        )
        for plugin in self._plugins:
            plugin.on_service_start(self, invocation)

        try:
            # 🎁 Prepare a synthetic event for the service.
            invoke_event = Event(
                f"invoke.{invocation.id}", {"input": invocation.input or {}}
            )
            # 🚀 Execute the synchronous service.
            result = service(self, self.context, invoke_event)
            # ✅ On success, immediately queue a 'done' event with the result.
            done_event = DoneEvent(
                f"done.invoke.{invocation.id}", data=result, src=invocation.id
            )
            self.send(done_event)
            logger.info(
                "✅ Sync service '%s' completed successfully.", invocation.src
            )
            for plugin in self._plugins:
                plugin.on_service_done(self, invocation, result)

        except Exception as e:
            # 💥 On failure, immediately queue an 'error' event with the exception.
            logger.error(
                "💔 Sync service '%s' failed: %s",
                invocation.src,
                e,
                exc_info=True,
            )
            error_event = DoneEvent(
                f"error.platform.{invocation.id}", data=e, src=invocation.id
            )
            self.send(error_event)
            for plugin in self._plugins:
                plugin.on_service_error(self, invocation, e)

    # -------------------------------------------------------------------------
    # 🛠️ Helper & Utility Methods (Private)
    # -------------------------------------------------------------------------

    def _resolve_target_state_robustly(
        self, transition: TransitionDefinition
    ) -> StateNode:
        """Resolves a target state string into a StateNode object robustly.

        This method attempts multiple resolution strategies in a specific order
        to provide flexibility in how transitions are defined in the machine.

        Args:
            transition: The transition containing the target string.

        Returns:
            The resolved `StateNode` object.

        Raises:
            StateNotFoundError: If the target state cannot be found after all attempts.
            ValueError: If the target string is empty for an external transition.
        """
        target_str = transition.target_str
        if not target_str:
            raise ValueError("Target string cannot be empty for resolution.")

        root, source = self.machine, transition.source
        parent = source.parent
        logger.debug(
            "🔄 Resolving target state: '%s' from source '%s'",
            target_str,
            source.id,
        )

        # 1️⃣ Standard resolution (relative to source, parent, root, and absolute)
        # This logic is restored from the original implementation to fix the regression.
        attempts = [
            (target_str, source),
            (target_str, parent) if parent else None,
            (target_str, root),
            (f"{root.id}.{target_str}", root),  # Absolute from root
        ]
        for tgt, ref in filter(None, attempts):
            try:
                state = resolve_target_state(tgt, ref)
                logger.debug(
                    "✅ Resolved '%s' via standard method from '%s'.",
                    tgt,
                    ref.id,
                )
                # ‼️ CRITICAL: This mutation logic is restored from the original code.
                transition.target_str = tgt
                return state
            except StateNotFoundError:
                continue  # Try the next method

        # 2️⃣ Direct attribute lookup on root
        if hasattr(root, target_str) and isinstance(
            getattr(root, target_str), StateNode
        ):
            logger.debug(
                "✅ Resolved '%s' via root attribute lookup.", target_str
            )
            return getattr(root, target_str)

        # 3️⃣ Root states dictionary lookup
        if hasattr(root, "states"):
            states_dict = root.states
            if target_str in states_dict:
                logger.debug(
                    "✅ Resolved '%s' via root states dictionary key.",
                    target_str,
                )
                return states_dict[target_str]
            for state in states_dict.values():
                if state.id.split(".")[-1] == target_str:
                    logger.debug(
                        "✅ Resolved '%s' via local name in states dict.",
                        target_str,
                    )
                    return state

        # 4️⃣ Depth-first tree walk fallback (match local ID part)
        for candidate in self._walk_tree(root):
            if candidate.id.split(".")[-1] == target_str:
                logger.debug(
                    "✅ Resolved '%s' via deep tree walk to find '%s'.",
                    target_str,
                    candidate.id,
                )
                return candidate

        # 🔚 Absolute failure
        available_toplevel = list(root.states.keys())
        logger.error(
            "❌ All resolution attempts failed for target: '%s'. Available top-level states: %s",
            target_str,
            available_toplevel,
        )
        raise StateNotFoundError(target_str, root.id)

    # -------------------------------------------------------------------------
    # 🛠️ Static Helper Methods
    # -------------------------------------------------------------------------

    @staticmethod
    def _is_async_callable(callable_obj: Callable[..., Any]) -> bool:
        """Checks if a callable is an async function (`async def`).

        This helper is used to prevent async logic from being run by the
        synchronous interpreter, which would cause runtime errors.

        Args:
            callable_obj: The function or method to check.

        Returns:
            True if the callable is an awaitable coroutine, False otherwise.
        """
        # A coroutine function's code object has the CO_COROUTINE flag set.
        return hasattr(callable_obj, "__code__") and (
            callable_obj.__code__.co_flags & 0x80  # noqa
        )

    @staticmethod
    def _walk_tree(node: StateNode) -> "SyncInterpreter._walk_tree":
        """Recursively yields all nodes in a state tree using depth-first traversal.

        This is a generator function used as a fallback mechanism for resolving
        state targets when standard resolution methods fail.

        Args:
            node: The root `StateNode` from which to start the traversal.

        Yields:
            Each `StateNode` in the tree, starting with the root.
        """
        # 🚶‍♂️ Yield the current node first
        yield node
        # 🌳 If the node has children, recurse into them
        if hasattr(node, "states"):
            for child in node.states.values():
                yield from SyncInterpreter._walk_tree(child)
