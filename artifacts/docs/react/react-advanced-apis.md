---
title: React Advanced Apis
source: react.dev
syllabus_weeks: [7, 8]
topics: [use, useOptimistic, useActionState, useId, useSyncExternalStore, cache, captureOwnerStack, Fragment, act]
---



# Use

`use` is a React API that lets you read the value of a resource like a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) or [context](/learn/passing-data-deeply-with-context).

```js
const value = use(resource);
```

<InlineToc />

---

## Reference {/*reference*/}

### `use(resource)` {/*use*/}

Call `use` in your component to read the value of a resource like a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) or [context](/learn/passing-data-deeply-with-context).

```jsx
import { use } from 'react';

function MessageComponent({ messagePromise }) {
  const message = use(messagePromise);
  const theme = use(ThemeContext);
  // ...
```

Unlike React Hooks, `use` can be called within loops and conditional statements like `if`. Like React Hooks, the function that calls `use` must be a Component or Hook.

When called with a Promise, the `use` API integrates with [`Suspense`](/reference/react/Suspense) and [Error Boundaries](/reference/react/Component#catching-rendering-errors-with-an-error-boundary). The component calling `use` *suspends* while the Promise passed to `use` is pending. If the component that calls `use` is wrapped in a Suspense boundary, the fallback will be displayed.  Once the Promise is resolved, the Suspense fallback is replaced by the rendered components using the data returned by the `use` API. If the Promise passed to `use` is rejected, the fallback of the nearest Error Boundary will be displayed.

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `resource`: this is the source of the data you want to read a value from. A resource can be a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) or a [context](/learn/passing-data-deeply-with-context).

#### Returns {/*returns*/}

The `use` API returns the value that was read from the resource like the resolved value of a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) or [context](/learn/passing-data-deeply-with-context).

#### Caveats {/*caveats*/}

* The `use` API must be called inside a Component or a Hook.
* When fetching data in a [Server Component](/reference/rsc/server-components), prefer `async` and `await` over `use`. `async` and `await` pick up rendering from the point where `await` was invoked, whereas `use` re-renders the component after the data is resolved.
* Prefer creating Promises in [Server Components](/reference/rsc/server-components) and passing them to [Client Components](/reference/rsc/use-client) over creating Promises in Client Components. Promises created in Client Components are recreated on every render. Promises passed from a Server Component to a Client Component are stable across re-renders. [See this example](#streaming-data-from-server-to-client).

---

## Usage {/*usage*/}

### Reading context with `use` {/*reading-context-with-use*/}

When a [context](/learn/passing-data-deeply-with-context) is passed to `use`, it works similarly to [`useContext`](/reference/react/useContext). While `useContext` must be called at the top level of your component, `use` can be called inside conditionals like `if` and loops like `for`. `use` is preferred over `useContext` because it is more flexible.

```js [[2, 4, "theme"], [1, 4, "ThemeContext"]]
import { use } from 'react';

function Button() {
  const theme = use(ThemeContext);
  // ... 
```

`use` returns the context value for the context you passed. To determine the context value, React searches the component tree and finds **the closest context provider above** for that particular context.

To pass context to a `Button`, wrap it or one of its parent components into the corresponding context provider.

```js [[1, 3, "ThemeContext"], [2, 3, "\\"dark\\""], [1, 5, "ThemeContext"]]
function MyPage() {
  return (
    <ThemeContext value="dark">
      <Form />
    </ThemeContext>
  );
}

function Form() {
  // ... renders buttons inside ...
}
```

It doesn't matter how many layers of components there are between the provider and the `Button`. When a `Button` *anywhere* inside of `Form` calls `use(ThemeContext)`, it will receive `"dark"` as the value.

Unlike [`useContext`](/reference/react/useContext), `use` can be called in conditionals and loops like `if`.

```js [[1, 2, "if"], [2, 3, "use"]]
function HorizontalRule({ show }) {
  if (show) {
    const theme = use(ThemeContext);
    return <hr className={theme} />;
  }
  return false;
}
```

`use` is called from inside a `if` statement, allowing you to conditionally read values from a Context.

> **Pitfall:**
>
> 
> 
> Like `useContext`, `use(context)` always looks for the closest context provider *above* the component that calls it. It searches upwards and **does not** consider context providers in the component from which you're calling `use(context)`.
> 
> 


[Interactive example removed — see react.dev for live demo]


### Streaming data from the server to the client {/*streaming-data-from-server-to-client*/}

Data can be streamed from the server to the client by passing a Promise as a prop from a Server Component to a Client Component.

```js [[1, 4, "App"], [2, 2, "Message"], [3, 7, "Suspense"], [4, 8, "messagePromise", 30], [4, 5, "messagePromise"]]
import { fetchMessage } from './lib.js';
import { Message } from './message.js';

export default function App() {
  const messagePromise = fetchMessage();
  return (
    <Suspense fallback={<p>waiting for message...</p>}>
      <Message messagePromise={messagePromise} />
    </Suspense>
  );
}
```

The Client Component then takes the Promise it received as a prop and passes it to the `use` API. This allows the Client Component to read the value from the Promise that was initially created by the Server Component.

```js [[2, 6, "Message"], [4, 6, "messagePromise"], [4, 7, "messagePromise"], [5, 7, "use"]]
// message.js
'use client';

import { use } from 'react';

export function Message({ messagePromise }) {
  const messageContent = use(messagePromise);
  return <p>Here is the message: {messageContent}</p>;
}
```
Because `Message` is wrapped in [`Suspense`](/reference/react/Suspense), the fallback will be displayed until the Promise is resolved. When the Promise is resolved, the value will be read by the `use` API and the `Message` component will replace the Suspense fallback.

[Interactive example removed — see react.dev for live demo]


> **Note:**
>
> 
> 
> When passing a Promise from a Server Component to a Client Component, its resolved value must be serializable to pass between server and client. Data types like functions aren't serializable and cannot be the resolved value of such a Promise.
> 
> 



> **Deep Dive: Should I resolve a Promise in a Server or Client Component? {/*resolve-promise-in-server-or-client-component*/}**
>
> A Promise can be passed from a Server Component to a Client Component and resolved in the Client Component with the `use` API. You can also resolve the Promise in a Server Component with `await` and pass the required data to the Client Component as a prop.
> 
> ```js
> export default async function App() {
>   const messageContent = await fetchMessage();
>   return <Message messageContent={messageContent} />
> }
> ```
> 
> But using `await` in a [Server Component](/reference/rsc/server-components) will block its rendering until the `await` statement is finished. Passing a Promise from a Server Component to a Client Component prevents the Promise from blocking the rendering of the Server Component.


### Dealing with rejected Promises {/*dealing-with-rejected-promises*/}

In some cases a Promise passed to `use` could be rejected. You can handle rejected Promises by either:

1. [Displaying an error to users with an Error Boundary.](#displaying-an-error-to-users-with-error-boundary)
2. [Providing an alternative value with `Promise.catch`](#providing-an-alternative-value-with-promise-catch)

> **Pitfall:**
>
> 
> `use` cannot be called in a try-catch block. Instead of a try-catch block [wrap your component in an Error Boundary](#displaying-an-error-to-users-with-error-boundary), or [provide an alternative value to use with the Promise's `.catch` method](#providing-an-alternative-value-with-promise-catch).
> 


#### Displaying an error to users with an Error Boundary {/*displaying-an-error-to-users-with-error-boundary*/}

If you'd like to display an error to your users when a Promise is rejected, you can use an [Error Boundary](/reference/react/Component#catching-rendering-errors-with-an-error-boundary). To use an Error Boundary, wrap the component where you are calling the `use` API in an Error Boundary. If the Promise passed to `use` is rejected the fallback for the Error Boundary will be displayed.

[Interactive example removed — see react.dev for live demo]


#### Providing an alternative value with `Promise.catch` {/*providing-an-alternative-value-with-promise-catch*/}

If you'd like to provide an alternative value when the Promise passed to `use` is rejected you can use the Promise's [`catch`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/catch) method.

```js [[1, 6, "catch"],[2, 7, "return"]]
import { Message } from './message.js';

export default function App() {
  const messagePromise = new Promise((resolve, reject) => {
    reject();
  }).catch(() => {
    return "no new message found.";
  });

  return (
    <Suspense fallback={<p>waiting for message...</p>}>
      <Message messagePromise={messagePromise} />
    </Suspense>
  );
}
```

To use the Promise's `catch` method, call `catch` on the Promise object. `catch` takes a single argument: a function that takes an error message as an argument. Whatever is returned by the function passed to `catch` will be used as the resolved value of the Promise.

---

## Troubleshooting {/*troubleshooting*/}

### "Suspense Exception: This is not a real error!" {/*suspense-exception-error*/}

You are either calling `use` outside of a React Component or Hook function, or calling `use` in a try–catch block. If you are calling `use` inside a try–catch block, wrap your component in an Error Boundary, or call the Promise's `catch` to catch the error and resolve the Promise with another value. [See these examples](#dealing-with-rejected-promises).

If you are calling `use` outside a React Component or Hook function, move the `use` call to a React Component or Hook function.

```jsx
function MessageComponent({messagePromise}) {
  function download() {
    // ❌ the function calling `use` is not a Component or Hook
    const message = use(messagePromise);
    // ...
```

Instead, call `use` outside any component closures, where the function that calls `use` is a Component or Hook.

```jsx
function MessageComponent({messagePromise}) {
  // ✅ `use` is being called from a component. 
  const message = use(messagePromise);
  // ...
```


# Useoptimistic

`useOptimistic` is a React Hook that lets you optimistically update the UI.

```js
const [optimisticState, setOptimistic] = useOptimistic(value, reducer?);
```

<InlineToc />

---

## Reference {/*reference*/}

### `useOptimistic(value, reducer?)` {/*useoptimistic*/}

Call `useOptimistic` at the top level of your component to create optimistic state for a value.

```js
import { useOptimistic } from 'react';

function MyComponent({name, todos}) {
  const [optimisticAge, setOptimisticAge] = useOptimistic(28);
  const [optimisticName, setOptimisticName] = useOptimistic(name);
  const [optimisticTodos, setOptimisticTodos] = useOptimistic(todos, todoReducer);
  // ...
}
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `value`: The value returned when there are no pending Actions.
* **optional** `reducer(currentState, action)`: The reducer function that specifies how the optimistic state gets updated. It must be pure, should take the current state and reducer action arguments, and should return the next optimistic state.

#### Returns {/*returns*/}

`useOptimistic` returns an array with exactly two values:

1. `optimisticState`: The current optimistic state. It is equal to `value` unless an Action is pending, in which case it is equal to the state returned by `reducer` (or the value passed to the set function if no `reducer` was provided).
2. The [`set` function](#setoptimistic) that lets you update the optimistic state to a different value inside an Action.

---

### `set` functions, like `setOptimistic(optimisticState)` {/*setoptimistic*/}

The `set` function returned by `useOptimistic` lets you update the state for the duration of an [Action](reference/react/useTransition#functions-called-in-starttransition-are-called-actions). You can pass the next state directly, or a function that calculates it from the previous state:

```js
const [optimisticLike, setOptimisticLike] = useOptimistic(false);
const [optimisticSubs, setOptimisticSubs] = useOptimistic(subs);

function handleClick() {
  startTransition(async () => {
    setOptimisticLike(true);
    setOptimisticSubs(a => a + 1);
    await saveChanges();
  });
}
```

#### Parameters {/*setoptimistic-parameters*/}

* `optimisticState`: The value that you want the optimistic state to be during an [Action](reference/react/useTransition#functions-called-in-starttransition-are-called-actions). If you provided a `reducer` to `useOptimistic`, this value will be passed as the second argument to your reducer. It can be a value of any type.
    * If you pass a function as `optimisticState`, it will be treated as an _updater function_. It must be pure, should take the pending state as its only argument, and should return the next optimistic state. React will put your updater function in a queue and re-render your component. During the next render, React will calculate the next state by applying the queued updaters to the previous state similar to [`useState` updaters](/reference/react/useState#setstate-parameters).

#### Returns {/*setoptimistic-returns*/}

`set` functions do not have a return value.

#### Caveats {/*setoptimistic-caveats*/}

* The `set` function must be called inside an [Action](reference/react/useTransition#functions-called-in-starttransition-are-called-actions). If you call the setter outside an Action, [React will show a warning](#an-optimistic-state-update-occurred-outside-a-transition-or-action) and the optimistic state will briefly render.

> **Deep Dive: How optimistic state works {/*how-optimistic-state-works*/}**
>
> `useOptimistic` lets you show a temporary value while a Action is in progress:
> 
> ```js
> const [value, setValue] = useState('a');
> const [optimistic, setOptimistic] = useOptimistic(value);
> 
> startTransition(async () => {
>   setOptimistic('b');
>   const newValue = await saveChanges('b');
>   setValue(newValue);
> });
> ```
> 
> When the setter is called inside an Action, `useOptimistic` will trigger a re-render to show that state while the Action is in progress. Otherwise, the `value` passed to `useOptimistic` is returned.
> 
> This state is called the "optimistic" because it is used to immediately present the user with the result of performing an Action, even though the Action actually takes time to complete.
> 
> **How the update flows**
> 
> 1. **Update immediately**: When `setOptimistic('b')` is called, React immediately renders with `'b'`.
> 
> 2. **(Optional) await in Action**: If you await in the Action, React continues showing `'b'`.
> 
> 3. **Transition scheduled**: `setValue(newValue)` schedules an update to the real state.
> 
> 4. **(Optional) wait for Suspense**: If `newValue` suspends, React continues showing `'b'`.
> 
> 5. **Single render commit**: Finally, the `newValue` commits for `value` and `optimistic`.
> 
> There's no extra render to "clear" the optimistic state. The optimistic and real state converge in the same render when the Transition completes.
> 
> <Note>
> 
> #### Optimistic state is temporary {/*optimistic-state-is-temporary*/}
> 
> Optimistic state only renders while an Action is in progress, otherwise `value` is rendered.
> 
> If `saveChanges` returned `'c'`, then both `value` and `optimistic` will be `'c'`, not `'b'`.
> 
> </Note>
> 
> **How the final state is determined**
> 
> The `value` argument to `useOptimistic` determines what displays after the Action finishes. How this works depends on the pattern you use:
> 
> - **Hardcoded values** like `useOptimistic(false)`: After the Action, `state` is still `false`, so the UI shows `false`. This is useful for pending states where you always start from `false`.
> 
> - **Props or state passed in** like `useOptimistic(isLiked)`: If the parent updates `isLiked` during the Action, the new value is used after the Action completes. This is how the UI reflects the result of the Action.
> 
> - **Reducer pattern** like `useOptimistic(items, fn)`: If `items` changes while the Action is pending, React re-runs your `reducer` with the new `items` to recalculate the state. This keeps your optimistic additions on top of the latest data.
> 
> **What happens when the Action fails**
> 
> If the Action throws an error, the Transition still ends, and React renders with whatever `value` currently is. Since the parent typically only updates `value` on success, a failure means `value` hasn't changed, so the UI shows what it showed before the optimistic update. You can catch the error to show a message to the user.


---

## Usage {/*usage*/}

### Adding optimistic state to a component {/*adding-optimistic-state-to-a-component*/}

Call `useOptimistic` at the top level of your component to declare one or more optimistic states.

```js [[1, 4, "age"], [1, 5, "name"], [1, 6, "todos"], [2, 4, "optimisticAge"], [2, 5, "optimisticName"], [2, 6, "optimisticTodos"], [3, 4, "setOptimisticAge"], [3, 5, "setOptimisticName"], [3, 6, "setOptimisticTodos"], [4, 6, "reducer"]]
import { useOptimistic } from 'react';

function MyComponent({age, name, todos}) {
  const [optimisticAge, setOptimisticAge] = useOptimistic(age);
  const [optimisticName, setOptimisticName] = useOptimistic(name);
  const [optimisticTodos, setOptimisticTodos] = useOptimistic(todos, reducer);
  // ...
```

`useOptimistic` returns an array with exactly two items:

1. The optimistic state, initially set to the value provided.
2. The set function that lets you temporarily change the state during an [Action](reference/react/useTransition#functions-called-in-starttransition-are-called-actions).
   * If a reducer is provided, it will run before returning the optimistic state.

To use the optimistic state, call the `set` function inside an Action. 

Actions are functions called inside `startTransition`:

```js {3}
function onAgeChange(e) {
  startTransition(async () => {
    setOptimisticAge(42);
    const newAge = await postAge(42);
    setAge(newAge);
  });
}
```

React will render the optimistic state `42` first while the `age` remains the current age. The Action waits for POST, and then renders the `newAge` for both `age` and `optimisticAge`.

See [How optimistic state works](#how-optimistic-state-works) for a deep dive.

> **Note:**
>
> 
> 
> When using [Action props](/reference/react/useTransition#exposing-action-props-from-components), you can call the set function without `startTransition`:
> 
> ```js [[3, 2, "setOptimisticName"]]
> async function submitAction() {
>   setOptimisticName('Taylor');
>   await updateName('Taylor');
> }
> ```
> 
> This works because Action props are already called inside `startTransition`.
> 
> For an example, see: [Using optimistic state in Action props](#using-optimistic-state-in-action-props).
> 
> 


---

### Using optimistic state in Action props {/*using-optimistic-state-in-action-props*/}

In an [Action prop](/reference/react/useTransition#exposing-action-props-from-components), you can call the optimistic setter directly without `startTransition`.

This example sets optimistic state inside a `<form>` `submitAction` prop:

[Interactive example removed — see react.dev for live demo]


In this example, when the user submits the form, the `optimisticName` updates immediately to show the `newName` optimistically while the server request is in progress. When the request completes, `name` and `optimisticName` are rendered with the actual `updatedName` from the response.

> **Deep Dive: Why doesn't this need `startTransition`? {/*why-doesnt-this-need-starttransition*/}**
>
> By convention, props called inside `startTransition` are named with "Action".
> 
> Since `submitAction` is named with "Action", you know it's already called inside `startTransition`.
> 
> See [Exposing `action` prop from components](/reference/react/useTransition#exposing-action-props-from-components) for the Action prop pattern.


---

### Adding optimistic state to Action props {/*adding-optimistic-state-to-action-props*/}

When creating an [Action prop](/reference/react/useTransition#exposing-action-props-from-components), you can add `useOptimistic` to show immediate feedback.

Here's a button that shows "Submitting..." while the `action` is pending:

[Interactive example removed — see react.dev for live demo]


When the button is clicked, `setIsPending(true)` uses optimistic state to immediately show "Submitting..." and disable the button. When the Action is done, `isPending` is rendered as `false` automatically.

This pattern automatically shows a pending state however `action` prop is used with `Button`:

```js
// Show pending state for a state update
<Button action={() => { setState(c => c + 1) }} />

// Show pending state for a navigation
<Button action={() => { navigate('/done') }} />

// Show pending state for a POST
<Button action={async () => { await fetch(/* ... */) }} />

// Show pending state for any combination
<Button action={async () => {
  setState(c => c + 1);
  await fetch(/* ... */);
  navigate('/done');
}} />
```

The pending state will be shown until everything in the `action` prop is finished.

> **Note:**
>
> 
> 
> You can also use [`useTransition`](/reference/react/useTransition) to get pending state via `isPending`. 
> 
> The difference is that `useTransition` gives you the `startTransition` function, while `useOptimistic` works with any Transition. Use whichever fits your component's needs.
> 
> 


---

### Updating props or state optimistically {/*updating-props-or-state-optimistically*/}

You can wrap props or state in `useOptimistic` to update it immediately while an Action is in progress.

In this example, `LikeButton` receives `isLiked` as a prop and immediately toggles it when clicked:

[Interactive example removed — see react.dev for live demo]


When the button is clicked, `setOptimisticIsLiked` immediately updates the displayed state to show the heart as liked. Meanwhile, `await toggleLike` runs in the background. When the `await` completes, `setIsLiked` parent updates the "real" `isLiked` state, and the optimistic state is rendered to match this new value.

> **Note:**
>
> 
> 
> This example reads from `optimisticIsLiked` to calculate the next value. This works when the base state won't change, but if the base state might change while your Action is pending, you may want to use a state updater or the reducer.
> 
> See [Updating state based on the current state](#updating-state-based-on-current-state) for an example.
> 
> 


---

### Updating multiple values together {/*updating-multiple-values-together*/}

When an optimistic update affects multiple related values, use a reducer to update them together. This ensures the UI stays consistent. 

Here's a follow button that updates both the follow state and follower count:

[Interactive example removed — see react.dev for live demo]


The reducer receives the new `isFollowing` value and calculates both the new follow state and the updated follower count in a single update. This ensures the button text and count always stay in sync.


> **Deep Dive: Choosing between updaters and reducers {/*choosing-between-updaters-and-reducers*/}**
>
> `useOptimistic` supports two patterns for calculating state based on current state:
> 
> **Updater functions** work like [useState updaters](/reference/react/useState#updating-state-based-on-the-previous-state). Pass a function to the setter:
> 
> ```js
> const [optimistic, setOptimistic] = useOptimistic(value);
> setOptimistic(current => !current);
> ```
> 
> **Reducers** separate the update logic from the setter call:
> 
> ```js
> const [optimistic, dispatch] = useOptimistic(value, (current, action) => {
>   // Calculate next state based on current and action
> });
> dispatch(action);
> ```
> 
> **Use updaters** for calculations where the setter call naturally describes the update. This is similar to using `setState(prev => ...)` with `useState`.
> 
> **Use reducers** when you need to pass data to the update (like which item to add) or when handling multiple types of updates with a single hook.
> 
> **Why use a reducer?**
> 
> Reducers are essential when the base state might change while your Transition is pending. If `todos` changes while your add is pending (for example, another user added a todo), React will re-run your reducer with the new `todos` to recalculate what to show. This ensures your new todo is added to the latest list, not an outdated copy.
> 
> An updater function like `setOptimistic(prev => [...prev, newItem])` would only see the state from when the Transition started, missing any updates that happened during the async work.


---

### Optimistically adding to a list {/*optimistically-adding-to-a-list*/}

When you need to optimistically add items to a list, use a `reducer`:

[Interactive example removed — see react.dev for live demo]


The `reducer` receives the current list of todos and the new todo to add. This is important because if the `todos` prop changes while your add is pending (for example, another user added a todo), React will update your optimistic state by re-running the reducer with the updated list. This ensures your new todo is added to the latest list, not an outdated copy.

> **Note:**
>
> 
> 
> Each optimistic item includes a `pending: true` flag so you can show loading state for individual items. When the server responds and the parent updates the canonical `todos` list with the saved item, the optimistic state updates to the confirmed item without the pending flag.
> 
> 


---

### Handling multiple `action` types {/*handling-multiple-action-types*/}

When you need to handle multiple types of optimistic updates (like adding and removing items), use a reducer pattern with `action` objects. 

This shopping cart example shows how to handle add and remove with a single reducer:

[Interactive example removed — see react.dev for live demo]


The reducer handles three `action` types (`add`, `remove`, `update_quantity`) and returns the new optimistic state for each. Each `action` sets a `pending: true` flag so you can show visual feedback while the [Server Function](/reference/rsc/server-functions) runs.

---

### Optimistic delete with error recovery {/*optimistic-delete-with-error-recovery*/}

When deleting items optimistically, you should handle the case where the Action fails.

This example shows how to display an error message when a delete fails, and the UI automatically rolls back to show the item again.

[Interactive example removed — see react.dev for live demo]


Try deleting 'Deploy to production'. When the delete fails, the item automatically reappears in the list. 

---

## Troubleshooting {/*troubleshooting*/}

### I'm getting an error: "An optimistic state update occurred outside a Transition or Action" {/*an-optimistic-state-update-occurred-outside-a-transition-or-action*/}

You may see this error:

<ConsoleBlockMulti>

<ConsoleLogLine level="error">

An optimistic state update occurred outside a Transition or Action. To fix, move the update to an Action, or wrap with `startTransition`.

</ConsoleLogLine>

</ConsoleBlockMulti>

The optimistic setter function must be called inside `startTransition`: 

```js
// 🚩 Incorrect: outside a Transition
function handleClick() {
  setOptimistic(newValue);  // Warning!
  // ...
}

// ✅ Correct: inside a Transition
function handleClick() {
  startTransition(async () => {
    setOptimistic(newValue);
    // ...
  });
}

// ✅ Also correct: inside an Action prop
function submitAction(formData) {
  setOptimistic(newValue);
  // ...
}
```

When you call the setter outside an Action, the optimistic state will briefly appear and then immediately revert back to the original value. This happens because there's no Transition to "hold" the optimistic state while your Action runs.

### I'm getting an error: "Cannot update optimistic state while rendering" {/*cannot-update-optimistic-state-while-rendering*/}

You may see this error:

<ConsoleBlockMulti>

<ConsoleLogLine level="error">

Cannot update optimistic state while rendering.

</ConsoleLogLine>

</ConsoleBlockMulti>

This error occurs when you call the optimistic setter during the render phase of a component. You can only call it from event handlers, effects, or other callbacks:

```js
// 🚩 Incorrect: calling during render
function MyComponent({ items }) {
  const [isPending, setPending] = useOptimistic(false);

  // This runs during render - not allowed!
  setPending(true);
  
  // ...
}

// ✅ Correct: calling inside startTransition
function MyComponent({ items }) {
  const [isPending, setPending] = useOptimistic(false);

  function handleClick() {
    startTransition(() => {
      setPending(true);
      // ...
    });
  }

  // ...
}

// ✅ Also correct: calling from an Action
function MyComponent({ items }) {
  const [isPending, setPending] = useOptimistic(false);

  function action() {
    setPending(true);
    // ...
  }

  // ...
}
```

### My optimistic updates show stale values {/*my-optimistic-updates-show-stale-values*/}

If your optimistic state seems to be based on old data, consider using an updater function or reducer to calculate the optimistic state relative to the current state.

```js
// May show stale data if state changes during Action
const [optimistic, setOptimistic] = useOptimistic(count);
setOptimistic(5);  // Always sets to 5, even if count changed

// Better: relative updates handle state changes correctly
const [optimistic, adjust] = useOptimistic(count, (current, delta) => current + delta);
adjust(1);  // Always adds 1 to whatever the current count is
```

See [Updating state based on the current state](#updating-state-based-on-current-state) for details.

### I don't know if my optimistic update is pending {/*i-dont-know-if-my-optimistic-update-is-pending*/}

To know when `useOptimistic` is pending, you have three options:

1. **Check if `optimisticValue === value`**

```js
const [optimistic, setOptimistic] = useOptimistic(value);
const isPending = optimistic !== value;
```

If the values are not equal, there's a Transition in progress.

2. **Add a `useTransition`**

```js
const [isPending, startTransition] = useTransition();
const [optimistic, setOptimistic] = useOptimistic(value);

//...
startTransition(() => {
  setOptimistic(state);
})
```

Since `useTransition` uses `useOptimistic` for `isPending` under the hood, this is equivalent to option 1.

3. **Add a `pending` flag in your reducer**

```js
const [optimistic, addOptimistic] = useOptimistic(
  items,
  (state, newItem) => [...state, { ...newItem, isPending: true }]
);
```

Since each optimistic item has its own flag, you can show loading state for individual items.


# Useactionstate

`useActionState` is a React Hook that lets you update state with side effects using [Actions](/reference/react/useTransition#functions-called-in-starttransition-are-called-actions).

```js
const [state, dispatchAction, isPending] = useActionState(reducerAction, initialState, permalink?);
```

<InlineToc />

---

## Reference {/*reference*/}

### `useActionState(reducerAction, initialState, permalink?)` {/*useactionstate*/}

Call `useActionState` at the top level of your component to create state for the result of an Action.

```js
import { useActionState } from 'react';

function reducerAction(previousState, actionPayload) {
  // ...
}

function MyCart({initialState}) {
  const [state, dispatchAction, isPending] = useActionState(reducerAction, initialState);
  // ...
}
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `reducerAction`: The function to be called when the Action is triggered. When called, it receives the previous state (initially the `initialState` you provided, then its previous return value) as its first argument, followed by the `actionPayload` passed to `dispatchAction`.
* `initialState`: The value you want the state to be initially. React ignores this argument after `dispatchAction` is invoked for the first time.
* **optional** `permalink`: A string containing the unique page URL that this form modifies.
  * For use on pages with [React Server Components](/reference/rsc/server-components) with progressive enhancement.
  * If `reducerAction` is a [Server Function](/reference/rsc/server-functions) and the form is submitted before the JavaScript bundle loads, the browser will navigate to the specified permalink URL rather than the current page's URL.

#### Returns {/*returns*/}

`useActionState` returns an array with exactly three values:

1. The current state. During the first render, it will match the `initialState` you passed. After `dispatchAction` is invoked, it will match the value returned by the `reducerAction`.
2. A `dispatchAction` function that you call inside [Actions](/reference/react/useTransition#functions-called-in-starttransition-are-called-actions).
3. The `isPending` flag that tells you if any dispatched Actions for this Hook are pending.

#### Caveats {/*caveats*/}

* `useActionState` is a Hook, so you can only call it **at the top level of your component** or your own Hooks. You can't call it inside loops or conditions. If you need that, extract a new component and move the state into it.
* React queues and executes multiple calls to `dispatchAction` sequentially. Each call to `reducerAction` receives the result of the previous call.
* The `dispatchAction` function has a stable identity, so you will often see it omitted from Effect dependencies, but including it will not cause the Effect to fire. If the linter lets you omit a dependency without errors, it is safe to do. [Learn more about removing Effect dependencies.](/learn/removing-effect-dependencies#move-dynamic-objects-and-functions-inside-your-effect)
* When using the `permalink` option, ensure the same form component is rendered on the destination page (including the same `reducerAction` and `permalink`) so React knows how to pass the state through. Once the page becomes interactive, this parameter has no effect.
* When using Server Functions, `initialState` needs to be [serializable](/reference/rsc/use-server#serializable-parameters-and-return-values) (values like plain objects, arrays, strings, and numbers).
* If `dispatchAction` throws an error, React cancels all queued actions and shows the nearest [Error Boundary](/reference/react/Component#catching-rendering-errors-with-an-error-boundary).
* If there are multiple ongoing Actions, React batches them together. This is a limitation that may be removed in a future release.

> **Note:**
>
> 
> 
> `dispatchAction` must be called from an Action. 
> 
> You can wrap it in [`startTransition`](/reference/react/startTransition), or pass it to an [Action prop](/reference/react/useTransition#exposing-action-props-from-components). Calls outside that scope won’t be treated as part of the Transition and [log an error](#async-function-outside-transition) on development mode.
> 
> 


---

### `reducerAction` function {/*reduceraction*/}

The `reducerAction` function passed to `useActionState` receives the previous state and returns a new state.

Unlike reducers in `useReducer`, the `reducerAction` can be async and perform side effects:

```js
async function reducerAction(previousState, actionPayload) {
  const newState = await post(actionPayload);
  return newState;
}
```

Each time you call `dispatchAction`, React calls the `reducerAction` with the `actionPayload`. The reducer will perform side effects such as posting data, and return the new state. If `dispatchAction` is called multiple times, React queues and executes them in order so the result of the previous call is passed as `previousState` for the current call.

#### Parameters {/*reduceraction-parameters*/}

* `previousState`: The last state. Initially this is equal to the `initialState`. After the first call to `dispatchAction`, it's equal to the last state returned.

* **optional** `actionPayload`: The argument passed to `dispatchAction`. It can be a value of any type. Similar to `useReducer` conventions, it is usually an object with a `type` property identifying it and, optionally, other properties with additional information.

#### Returns {/*reduceraction-returns*/}

`reducerAction` returns the new state, and triggers a Transition to re-render with that state.

#### Caveats {/*reduceraction-caveats*/}

* `reducerAction` can be sync or async. It can perform sync actions like showing a notification, or async actions like posting updates to a server. 
* `reducerAction` is not invoked twice in `<StrictMode>` since `reducerAction` is designed to allow side effects.
* The return type of `reducerAction` must match the type of `initialState`. If TypeScript infers a mismatch, you may need to explicitly annotate your state type.
* If you set state after `await` in the `reducerAction` you currently need to wrap the state update in an additional `startTransition`. See the [startTransition](/reference/react/useTransition#react-doesnt-treat-my-state-update-after-await-as-a-transition) docs for more info.
* When using Server Functions, `actionPayload` needs to be [serializable](/reference/rsc/use-server#serializable-parameters-and-return-values) (values like plain objects, arrays, strings, and numbers).

> **Deep Dive: Why is it called `reducerAction`? {/*why-is-it-called-reduceraction*/}**
>
> The function passed to `useActionState` is called a *reducer action* because:
> 
> - It *reduces* the previous state into a new state, like `useReducer`.
> - It's an *Action* because it's called inside a Transition and can perform side effects.
> 
> Conceptually, `useActionState` is like `useReducer`, but you can do side effects in the reducer.


---

## Usage {/*usage*/}

### Adding state to an Action {/*adding-state-to-an-action*/}

Call `useActionState` at the top level of your component to create state for the result of an Action.

```js [[1, 7, "count"], [2, 7, "dispatchAction"], [3, 7, "isPending"]]
import { useActionState } from 'react';

async function addToCartAction(prevCount) {
  // ...
}
function Counter() {
  const [count, dispatchAction, isPending] = useActionState(addToCartAction, 0);

  // ...
}
```

`useActionState` returns an array with exactly three items:

1. The current state, initially set to the initial state you provided.
2. The action dispatcher that lets you trigger `reducerAction`.
3. A pending state that tells you whether the Action is in progress.

To call `addToCartAction`, call the action dispatcher. React will queue calls to `addToCartAction` with the previous count.

[Interactive example removed — see react.dev for live demo]


Every time you click "Add Ticket," React queues a call to `addToCartAction`. React shows the pending state until all the tickets are added, and then re-renders with the final state.

> **Deep Dive: How `useActionState` queuing works {/*how-useactionstate-queuing-works*/}**
>
> Try clicking "Add Ticket" multiple times. Every time you click, a new `addToCartAction` is queued. Since there's an artificial 1 second delay, that means 4 clicks will take ~4 seconds to complete.
> 
> **This is intentional in the design of `useActionState`.**
> 
> We have to wait for the previous result of `addToCartAction` in order to pass the `prevCount` to the next call to `addToCartAction`. That means React has to wait for the previous Action to finish before calling the next Action. 
> 
> You can typically solve this by [using with useOptimistic](/reference/react/useActionState#using-with-useoptimistic) but for more complex cases you may want to consider [cancelling queued actions](#cancelling-queued-actions) or not using `useActionState`.


---

### Using multiple Action types {/*using-multiple-action-types*/}

To handle multiple types, you can pass an argument to `dispatchAction`.

By convention, it is common to write it as a switch statement. For each case in the switch, calculate and return some next state. The argument can have any shape, but it is common to pass objects with a `type` property identifying the action.

[Interactive example removed — see react.dev for live demo]


When you click to increase or decrease the quantity, an `"ADD"` or `"REMOVE"` is dispatched. In the `reducerAction`, different APIs are called to update the quantity.

In this example, we use the pending state of the Actions to replace both the quantity and the total. If you want to provide immediate feedback, such as immediately updating the quantity, you can use `useOptimistic`.

> **Deep Dive: How is `useActionState` different from `useReducer`? {/*useactionstate-vs-usereducer*/}**
>
> You might notice this example looks a lot like `useReducer`, but they serve different purposes:
> 
> - **Use `useReducer`** to manage state of your UI. The reducer must be pure.
> 
> - **Use `useActionState`** to manage state of your Actions. The reducer can perform side effects.
> 
> You can think of `useActionState` as `useReducer` for side effects from user Actions. Since it computes the next Action to take based on the previous Action, it has to [order the calls sequentially](/reference/react/useActionState#how-useactionstate-queuing-works). If you want to perform Actions in parallel, use `useState` and `useTransition` directly.


---

### Using with `useOptimistic` {/*using-with-useoptimistic*/}

You can combine `useActionState` with [`useOptimistic`](/reference/react/useOptimistic) to show immediate UI feedback:


[Interactive example removed — see react.dev for live demo]



`setOptimisticCount` immediately updates the quantity, and `dispatchAction()` queues the `updateCartAction`. A pending indicator appears on both the quantity and total to give the user feedback that their update is still being applied.

---


### Using with Action props {/*using-with-action-props*/}

When you pass the `dispatchAction` function to a component that exposes an [Action prop](/reference/react/useTransition#exposing-action-props-from-components), you don't need to call `startTransition` or `useOptimistic` yourself.

This example shows using the `increaseAction` and `decreaseAction` props of a QuantityStepper component:

[Interactive example removed — see react.dev for live demo]


Since `<QuantityStepper>` has built-in support for transitions, pending state, and optimistically updating the count, you just need to tell the Action _what_ to change, and _how_ to change it is handled for you.

---

### Cancelling queued Actions {/*cancelling-queued-actions*/}

You can use an `AbortController` to cancel pending Actions:

[Interactive example removed — see react.dev for live demo]


Try clicking increase or decrease multiple times, and notice that the total updates within 1 second no matter how many times you click. This works because it uses an `AbortController` to "complete" the previous Action so the next Action can proceed.

> **Pitfall:**
>
> 
> 
> Aborting an Action isn't always safe.
> 
> For example, if the Action performs a mutation (like writing to a database), aborting the network request doesn't undo the server-side change. This is why `useActionState` doesn't abort by default. It's only safe when you know the side effect can be safely ignored or retried.
> 
> 


---

### Using with `<form>` Action props {/*use-with-a-form*/}

You can pass the `dispatchAction` function as the `action` prop to a `<form>`.

When used this way, React automatically wraps the submission in a Transition, so you don't need to call `startTransition` yourself. The `reducerAction` receives the previous state and the submitted `FormData`:

[Interactive example removed — see react.dev for live demo]


In this example, when the user clicks the stepper arrows, the button submits the form and `useActionState` calls `updateCartAction` with the form data. The example uses `useOptimistic` to immediately show the new quantity while the server confirms the update.

<RSC>

When used with a [Server Function](/reference/rsc/server-functions), `useActionState` allows the server's response to be shown before hydration (when React attaches to server-rendered HTML) completes. You can also use the optional `permalink` parameter for progressive enhancement (allowing the form to work before JavaScript loads) on pages with dynamic content. This is typically handled by your framework for you.

</RSC>

See the [`<form>`](/reference/react-dom/components/form#handle-form-submission-with-a-server-function) docs for more information on using Actions with forms. 

---

### Handling errors {/*handling-errors*/}

There are two ways to handle errors with `useActionState`.

For known errors, such as "quantity not available" validation errors from your backend, you can return it as part of your `reducerAction` state and display it in the UI.

For unknown errors, such as `undefined is not a function`, you can throw an error. React will cancel all queued Actions and shows the nearest [Error Boundary](/reference/react/Component#catching-rendering-errors-with-an-error-boundary) by rethrowing the error from the `useActionState` hook.

[Interactive example removed — see react.dev for live demo]


In this example, "Add 10" simulates an API that returns a validation error, which `updateCartAction` stores in state and displays inline. "Add NaN" results in an invalid count, so `updateCartAction` throws, which propagates through `useActionState` to the `ErrorBoundary` and shows a reset UI.


---

## Troubleshooting {/*troubleshooting*/}

### My `isPending` flag is not updating {/*ispending-not-updating*/}

If you're calling `dispatchAction` manually (not through an Action prop), make sure you wrap the call in [`startTransition`](/reference/react/startTransition):

```js
import { useActionState, startTransition } from 'react';

function MyComponent() {
  const [state, dispatchAction, isPending] = useActionState(myAction, null);

  function handleClick() {
    // ✅ Correct: wrap in startTransition
    startTransition(() => {
      dispatchAction();
    });
  }

  // ...
}
```

When `dispatchAction` is passed to an Action prop, React automatically wraps it in a Transition.

---

### My Action cannot read form data {/*action-cannot-read-form-data*/}

When you use `useActionState`, the `reducerAction` receives an extra argument as its first argument: the previous or initial state. The submitted form data is therefore its second argument instead of its first.

```js {2,7}
// Without useActionState
function action(formData) {
  const name = formData.get('name');
}

// With useActionState
function action(prevState, formData) {
  const name = formData.get('name');
}
```

---

### My actions are being skipped {/*actions-skipped*/}

If you call `dispatchAction` multiple times and some of them don't run, it may be because an earlier `dispatchAction` call threw an error.

When a `reducerAction` throws, React skips all subsequently queued `dispatchAction` calls.

To handle this, catch errors within your `reducerAction` and return an error state instead of throwing:

```js
async function myReducerAction(prevState, data) {
  try {
    const result = await submitData(data);
    return { success: true, data: result };
  } catch (error) {
    // ✅ Return error state instead of throwing
    return { success: false, error: error.message };
  }
}
```

---

### My state doesn't reset {/*reset-state*/}

`useActionState` doesn't provide a built-in reset function. To reset the state, you can design your `reducerAction` to handle a reset signal:

```js
const initialState = { name: '', error: null };

async function formAction(prevState, payload) {
  // Handle reset
  if (payload === null) {
    return initialState;
  }
  // Normal action logic
  const result = await submitData(payload);
  return result;
}

function MyComponent() {
  const [state, dispatchAction, isPending] = useActionState(formAction, initialState);

  function handleReset() {
    startTransition(() => {
      dispatchAction(null); // Pass null to trigger reset
    });
  }

  // ...
}
```

Alternatively, you can add a `key` prop to the component using `useActionState` to force it to remount with fresh state, or a `<form>` `action` prop, which resets automatically after submission.

---

### I'm getting an error: "An async function with useActionState was called outside of a transition." {/*async-function-outside-transition*/}

A common mistake is to forget to call `dispatchAction` from inside a Transition:

<ConsoleBlockMulti>
<ConsoleLogLine level="error">

An async function with useActionState was called outside of a transition. This is likely not what you intended (for example, isPending will not update correctly). Either call the returned function inside startTransition, or pass it to an `action` or `formAction` prop.

</ConsoleLogLine>
</ConsoleBlockMulti>


This error happens because `dispatchAction` must run inside a Transition:

```js
function MyComponent() {
  const [state, dispatchAction, isPending] = useActionState(myAsyncAction, null);

  function handleClick() {
    // ❌ Wrong: calling dispatchAction outside a Transition
    dispatchAction();
  }

  // ...
}
```

To fix, either wrap the call in [`startTransition`](/reference/react/startTransition):

```js
import { useActionState, startTransition } from 'react';

function MyComponent() {
  const [state, dispatchAction, isPending] = useActionState(myAsyncAction, null);

  function handleClick() {
    // ✅ Correct: wrap in startTransition
    startTransition(() => {
      dispatchAction();
    });
  }

  // ...
}
```

Or pass `dispatchAction` to an Action prop, is call in a Transition:

```js
function MyComponent() {
  const [state, dispatchAction, isPending] = useActionState(myAsyncAction, null);

  // ✅ Correct: action prop wraps in a Transition for you
  return <Button action={dispatchAction}>...</Button>;
}
```

---

### I'm getting an error: "Cannot update action state while rendering" {/*cannot-update-during-render*/}

You cannot call `dispatchAction` during render:

<ConsoleBlock level="error">

Cannot update action state while rendering.

</ConsoleBlock>

This causes an infinite loop because calling `dispatchAction` schedules a state update, which triggers a re-render, which calls `dispatchAction` again.

```js
function MyComponent() {
  const [state, dispatchAction, isPending] = useActionState(myAction, null);

  // ❌ Wrong: calling dispatchAction during render
  dispatchAction();

  // ...
}
```

To fix, only call `dispatchAction` in response to user events (like form submissions or button clicks).


# Useid

`useId` is a React Hook for generating unique IDs that can be passed to accessibility attributes.

```js
const id = useId()
```

<InlineToc />

---

## Reference {/*reference*/}

### `useId()` {/*useid*/}

Call `useId` at the top level of your component to generate a unique ID:

```js
import { useId } from 'react';

function PasswordField() {
  const passwordHintId = useId();
  // ...
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

`useId` does not take any parameters.

#### Returns {/*returns*/}

`useId` returns a unique ID string associated with this particular `useId` call in this particular component.

#### Caveats {/*caveats*/}

* `useId` is a Hook, so you can only call it **at the top level of your component** or your own Hooks. You can't call it inside loops or conditions. If you need that, extract a new component and move the state into it.

* `useId` **should not be used to generate cache keys** for [use()](/reference/react/use). The ID is stable when a component is mounted but may change during rendering. Cache keys should be generated from your data.

* `useId` **should not be used to generate keys** in a list. [Keys should be generated from your data.](/learn/rendering-lists#where-to-get-your-key)

* `useId` currently cannot be used in [async Server Components](/reference/rsc/server-components#async-components-with-server-components).

---

## Usage {/*usage*/}

> **Pitfall:**
>
> 
> 
> **Do not call `useId` to generate keys in a list.** [Keys should be generated from your data.](/learn/rendering-lists#where-to-get-your-key)
> 
> 


### Generating unique IDs for accessibility attributes {/*generating-unique-ids-for-accessibility-attributes*/}

Call `useId` at the top level of your component to generate a unique ID:

```js [[1, 4, "passwordHintId"]]
import { useId } from 'react';

function PasswordField() {
  const passwordHintId = useId();
  // ...
```

You can then pass the generated ID to different attributes:

```js [[1, 2, "passwordHintId"], [1, 3, "passwordHintId"]]
<>
  <input type="password" aria-describedby={passwordHintId} />
  <p id={passwordHintId}>
</>
```

**Let's walk through an example to see when this is useful.**

[HTML accessibility attributes](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA) like [`aria-describedby`](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-describedby) let you specify that two tags are related to each other. For example, you can specify that an element (like an input) is described by another element (like a paragraph).

In regular HTML, you would write it like this:

```html {5,8}
<label>
  Password:
  <input
    type="password"
    aria-describedby="password-hint"
  />
</label>
<p id="password-hint">
  The password should contain at least 18 characters
</p>
```

However, hardcoding IDs like this is not a good practice in React. A component may be rendered more than once on the page--but IDs have to be unique! Instead of hardcoding an ID, generate a unique ID with `useId`:

```js {4,11,14}
import { useId } from 'react';

function PasswordField() {
  const passwordHintId = useId();
  return (
    <>
      <label>
        Password:
        <input
          type="password"
          aria-describedby={passwordHintId}
        />
      </label>
      <p id={passwordHintId}>
        The password should contain at least 18 characters
      </p>
    </>
  );
}
```

Now, even if `PasswordField` appears multiple times on the screen, the generated IDs won't clash.

[Interactive example removed — see react.dev for live demo]


[Watch this video](https://www.youtube.com/watch?v=0dNzNcuEuOo) to see the difference in the user experience with assistive technologies.

> **Pitfall:**
>
> 
> 
> With [server rendering](/reference/react-dom/server), **`useId` requires an identical component tree on the server and the client**. If the trees you render on the server and the client don't match exactly, the generated IDs won't match.
> 
> 


> **Deep Dive: Why is useId better than an incrementing counter? {/*why-is-useid-better-than-an-incrementing-counter*/}**
>
> You might be wondering why `useId` is better than incrementing a global variable like `nextId++`.
> 
> The primary benefit of `useId` is that React ensures that it works with [server rendering.](/reference/react-dom/server) During server rendering, your components generate HTML output. Later, on the client, [hydration](/reference/react-dom/client/hydrateRoot) attaches your event handlers to the generated HTML. For hydration to work, the client output must match the server HTML.
> 
> This is very difficult to guarantee with an incrementing counter because the order in which the Client Components are hydrated may not match the order in which the server HTML was emitted. By calling `useId`, you ensure that hydration will work, and the output will match between the server and the client.
> 
> Inside React, `useId` is generated from the "parent path" of the calling component. This is why, if the client and the server tree are the same, the "parent path" will match up regardless of rendering order.


---

### Generating IDs for several related elements {/*generating-ids-for-several-related-elements*/}

If you need to give IDs to multiple related elements, you can call `useId` to generate a shared prefix for them: 

[Interactive example removed — see react.dev for live demo]


This lets you avoid calling `useId` for every single element that needs a unique ID.

---

### Specifying a shared prefix for all generated IDs {/*specifying-a-shared-prefix-for-all-generated-ids*/}

If you render multiple independent React applications on a single page, pass `identifierPrefix` as an option to your [`createRoot`](/reference/react-dom/client/createRoot#parameters) or [`hydrateRoot`](/reference/react-dom/client/hydrateRoot) calls. This ensures that the IDs generated by the two different apps never clash because every identifier generated with `useId` will start with the distinct prefix you've specified.

[Interactive example removed — see react.dev for live demo]


---

### Using the same ID prefix on the client and the server {/*using-the-same-id-prefix-on-the-client-and-the-server*/}

If you [render multiple independent React apps on the same page](#specifying-a-shared-prefix-for-all-generated-ids), and some of these apps are server-rendered, make sure that the `identifierPrefix` you pass to the [`hydrateRoot`](/reference/react-dom/client/hydrateRoot) call on the client side is the same as the `identifierPrefix` you pass to the [server APIs](/reference/react-dom/server) such as [`renderToPipeableStream`.](/reference/react-dom/server/renderToPipeableStream)

```js
// Server
import { renderToPipeableStream } from 'react-dom/server';

const { pipe } = renderToPipeableStream(
  <App />,
  { identifierPrefix: 'react-app1' }
);
```

```js
// Client
import { hydrateRoot } from 'react-dom/client';

const domNode = document.getElementById('root');
const root = hydrateRoot(
  domNode,
  reactNode,
  { identifierPrefix: 'react-app1' }
);
```

You do not need to pass `identifierPrefix` if you only have one React app on the page.


# Usesyncexternalstore

`useSyncExternalStore` is a React Hook that lets you subscribe to an external store.

```js
const snapshot = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot?)` {/*usesyncexternalstore*/}

Call `useSyncExternalStore` at the top level of your component to read a value from an external data store.

```js
import { useSyncExternalStore } from 'react';
import { todosStore } from './todoStore.js';

function TodosApp() {
  const todos = useSyncExternalStore(todosStore.subscribe, todosStore.getSnapshot);
  // ...
}
```

It returns the snapshot of the data in the store. You need to pass two functions as arguments:

1. The `subscribe` function should subscribe to the store and return a function that unsubscribes.
2. The `getSnapshot` function should read a snapshot of the data from the store.

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `subscribe`: A function that takes a single `callback` argument and subscribes it to the store. When the store changes, it should invoke the provided `callback`, which will cause React to re-call `getSnapshot` and (if needed) re-render the component. The `subscribe` function should return a function that cleans up the subscription.

* `getSnapshot`: A function that returns a snapshot of the data in the store that's needed by the component. While the store has not changed, repeated calls to `getSnapshot` must return the same value. If the store changes and the returned value is different (as compared by [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is)), React re-renders the component.

* **optional** `getServerSnapshot`: A function that returns the initial snapshot of the data in the store. It will be used only during server rendering and during hydration of server-rendered content on the client. The server snapshot must be the same between the client and the server, and is usually serialized and passed from the server to the client. If you omit this argument, rendering the component on the server will throw an error.

#### Returns {/*returns*/}

The current snapshot of the store which you can use in your rendering logic.

#### Caveats {/*caveats*/}

* The store snapshot returned by `getSnapshot` must be immutable. If the underlying store has mutable data, return a new immutable snapshot if the data has changed. Otherwise, return a cached last snapshot.

* If a different `subscribe` function is passed during a re-render, React will re-subscribe to the store using the newly passed `subscribe` function. You can prevent this by declaring `subscribe` outside the component.

* If the store is mutated during a [non-blocking Transition update](/reference/react/useTransition), React will fall back to performing that update as blocking. Specifically, for every Transition update, React will call `getSnapshot` a second time just before applying changes to the DOM. If it returns a different value than when it was called originally, React will restart the update from scratch, this time applying it as a blocking update, to ensure that every component on screen is reflecting the same version of the store.

* It's not recommended to _suspend_ a render based on a store value returned by `useSyncExternalStore`. The reason is that mutations to the external store cannot be marked as [non-blocking Transition updates](/reference/react/useTransition), so they will trigger the nearest [`Suspense` fallback](/reference/react/Suspense), replacing already-rendered content on screen with a loading spinner, which typically makes a poor UX.

  For example, the following are discouraged:

  ```js
  const LazyProductDetailPage = lazy(() => import('./ProductDetailPage.js'));

  function ShoppingApp() {
    const selectedProductId = useSyncExternalStore(...);

    // ❌ Calling `use` with a Promise dependent on `selectedProductId`
    const data = use(fetchItem(selectedProductId))

    // ❌ Conditionally rendering a lazy component based on `selectedProductId`
    return selectedProductId != null ? <LazyProductDetailPage /> : <FeaturedProducts />;
  }
  ```

---

## Usage {/*usage*/}

### Subscribing to an external store {/*subscribing-to-an-external-store*/}

Most of your React components will only read data from their [props,](/learn/passing-props-to-a-component) [state,](/reference/react/useState) and [context.](/reference/react/useContext) However, sometimes a component needs to read some data from some store outside of React that changes over time. This includes:

* Third-party state management libraries that hold state outside of React.
* Browser APIs that expose a mutable value and events to subscribe to its changes.

Call `useSyncExternalStore` at the top level of your component to read a value from an external data store.

```js [[1, 5, "todosStore.subscribe"], [2, 5, "todosStore.getSnapshot"], [3, 5, "todos", 0]]
import { useSyncExternalStore } from 'react';
import { todosStore } from './todoStore.js';

function TodosApp() {
  const todos = useSyncExternalStore(todosStore.subscribe, todosStore.getSnapshot);
  // ...
}
```

It returns the snapshot of the data in the store. You need to pass two functions as arguments:

1. The `subscribe` function should subscribe to the store and return a function that unsubscribes.
2. The `getSnapshot` function should read a snapshot of the data from the store.

React will use these functions to keep your component subscribed to the store and re-render it on changes.

For example, in the sandbox below, `todosStore` is implemented as an external store that stores data outside of React. The `TodosApp` component connects to that external store with the `useSyncExternalStore` Hook. 

[Interactive example removed — see react.dev for live demo]


> **Note:**
>
> 
> 
> When possible, we recommend using built-in React state with [`useState`](/reference/react/useState) and [`useReducer`](/reference/react/useReducer) instead. The `useSyncExternalStore` API is mostly useful if you need to integrate with existing non-React code.
> 
> 


---

### Subscribing to a browser API {/*subscribing-to-a-browser-api*/}

Another reason to add `useSyncExternalStore` is when you want to subscribe to some value exposed by the browser that changes over time. For example, suppose that you want your component to display whether the network connection is active. The browser exposes this information via a property called [`navigator.onLine`.](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine)

This value can change without React's knowledge, so you should read it with `useSyncExternalStore`.

```js
import { useSyncExternalStore } from 'react';

function ChatIndicator() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);
  // ...
}
```

To implement the `getSnapshot` function, read the current value from the browser API:

```js
function getSnapshot() {
  return navigator.onLine;
}
```

Next, you need to implement the `subscribe` function. For example, when `navigator.onLine` changes, the browser fires the [`online`](https://developer.mozilla.org/en-US/docs/Web/API/Window/online_event) and [`offline`](https://developer.mozilla.org/en-US/docs/Web/API/Window/offline_event) events on the `window` object. You need to subscribe the `callback` argument to the corresponding events, and then return a function that cleans up the subscriptions:

```js
function subscribe(callback) {
  window.addEventListener('online', callback);
  window.addEventListener('offline', callback);
  return () => {
    window.removeEventListener('online', callback);
    window.removeEventListener('offline', callback);
  };
}
```

Now React knows how to read the value from the external `navigator.onLine` API and how to subscribe to its changes. Disconnect your device from the network and notice that the component re-renders in response:

[Interactive example removed — see react.dev for live demo]


---

### Extracting the logic to a custom Hook {/*extracting-the-logic-to-a-custom-hook*/}

Usually you won't write `useSyncExternalStore` directly in your components. Instead, you'll typically call it from your own custom Hook. This lets you use the same external store from different components.

For example, this custom `useOnlineStatus` Hook tracks whether the network is online:

```js {3,6}
import { useSyncExternalStore } from 'react';

export function useOnlineStatus() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);
  return isOnline;
}

function getSnapshot() {
  // ...
}

function subscribe(callback) {
  // ...
}
```

Now different components can call `useOnlineStatus` without repeating the underlying implementation:

[Interactive example removed — see react.dev for live demo]


---

### Adding support for server rendering {/*adding-support-for-server-rendering*/}

If your React app uses [server rendering,](/reference/react-dom/server) your React components will also run outside the browser environment to generate the initial HTML. This creates a few challenges when connecting to an external store:

- If you're connecting to a browser-only API, it won't work because it does not exist on the server.
- If you're connecting to a third-party data store, you'll need its data to match between the server and client.

To solve these issues, pass a `getServerSnapshot` function as the third argument to `useSyncExternalStore`:

```js {4,12-14}
import { useSyncExternalStore } from 'react';

export function useOnlineStatus() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  return isOnline;
}

function getSnapshot() {
  return navigator.onLine;
}

function getServerSnapshot() {
  return true; // Always show "Online" for server-generated HTML
}

function subscribe(callback) {
  // ...
}
```

The `getServerSnapshot` function is similar to `getSnapshot`, but it runs only in two situations:

- It runs on the server when generating the HTML.
- It runs on the client during [hydration](/reference/react-dom/client/hydrateRoot), i.e. when React takes the server HTML and makes it interactive.

This lets you provide the initial snapshot value which will be used before the app becomes interactive. If there is no meaningful initial value for the server rendering, omit this argument to [force rendering on the client.](/reference/react/Suspense#providing-a-fallback-for-server-errors-and-client-only-content)

> **Note:**
>
> 
> 
> Make sure that `getServerSnapshot` returns the same exact data on the initial client render as it returned on the server. For example, if `getServerSnapshot` returned some prepopulated store content on the server, you need to transfer this content to the client. One way to do this is to emit a `<script>` tag during server rendering that sets a global like `window.MY_STORE_DATA`, and read from that global on the client in `getServerSnapshot`. Your external store should provide instructions on how to do that.
> 
> 


---

## Troubleshooting {/*troubleshooting*/}

### I'm getting an error: "The result of `getSnapshot` should be cached" {/*im-getting-an-error-the-result-of-getsnapshot-should-be-cached*/}

This error means your `getSnapshot` function returns a new object every time it's called, for example:

```js {2-5}
function getSnapshot() {
  // 🔴 Do not return always different objects from getSnapshot
  return {
    todos: myStore.todos
  };
}
```

React will re-render the component if `getSnapshot` return value is different from the last time. This is why, if you always return a different value, you will enter an infinite loop and get this error.

Your `getSnapshot` object should only return a different object if something has actually changed. If your store contains immutable data, you can return that data directly:

```js {2-3}
function getSnapshot() {
  // ✅ You can return immutable data
  return myStore.todos;
}
```

If your store data is mutable, your `getSnapshot` function should return an immutable snapshot of it. This means it *does* need to create new objects, but it shouldn't do this for every single call. Instead, it should store the last calculated snapshot, and return the same snapshot as the last time if the data in the store has not changed. How you determine whether mutable data has changed depends on your mutable store.

---

### My `subscribe` function gets called after every re-render {/*my-subscribe-function-gets-called-after-every-re-render*/}

This `subscribe` function is defined *inside* a component so it is different on every re-render:

```js {2-5}
function ChatIndicator() {
  // 🚩 Always a different function, so React will resubscribe on every re-render
  function subscribe() {
    // ...
  }
  
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);

  // ...
}
```
  
React will resubscribe to your store if you pass a different `subscribe` function between re-renders. If this causes performance issues and you'd like to avoid resubscribing, move the `subscribe` function outside:

```js {1-4}
// ✅ Always the same function, so React won't need to resubscribe
function subscribe() {
  // ...
}

function ChatIndicator() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);
  // ...
}
```

Alternatively, wrap `subscribe` into [`useCallback`](/reference/react/useCallback) to only resubscribe when some argument changes:

```js {2-5}
function ChatIndicator({ userId }) {
  // ✅ Same function as long as userId doesn't change
  const subscribe = useCallback(() => {
    // ...
  }, [userId]);
  
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);

  // ...
}
```


# Cache

<RSC>

`cache` is only for use with [React Server Components](/reference/rsc/server-components).

</RSC>

`cache` lets you cache the result of a data fetch or computation.

```js
const cachedFn = cache(fn);
```

<InlineToc />

---

## Reference {/*reference*/}

### `cache(fn)` {/*cache*/}

Call `cache` outside of any components to create a version of the function with caching.

```js {4,7}
import {cache} from 'react';
import calculateMetrics from 'lib/metrics';

const getMetrics = cache(calculateMetrics);

function Chart({data}) {
  const report = getMetrics(data);
  // ...
}
```

When `getMetrics` is first called with `data`, `getMetrics` will call `calculateMetrics(data)` and store the result in cache. If `getMetrics` is called again with the same `data`, it will return the cached result instead of calling `calculateMetrics(data)` again.

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

- `fn`: The function you want to cache results for. `fn` can take any arguments and return any value.

#### Returns {/*returns*/}

`cache` returns a cached version of `fn` with the same type signature. It does not call `fn` in the process.

When calling `cachedFn` with given arguments, it first checks if a cached result exists in the cache. If a cached result exists, it returns the result. If not, it calls `fn` with the arguments, stores the result in the cache, and returns the result. The only time `fn` is called is when there is a cache miss.

> **Note:**
>
> 
> 
> The optimization of caching return values based on inputs is known as [_memoization_](https://en.wikipedia.org/wiki/Memoization). We refer to the function returned from `cache` as a memoized function.
> 
> 


#### Caveats {/*caveats*/}

- React will invalidate the cache for all memoized functions for each server request.
- Each call to `cache` creates a new function. This means that calling `cache` with the same function multiple times will return different memoized functions that do not share the same cache.
- `cachedFn` will also cache errors. If `fn` throws an error for certain arguments, it will be cached, and the same error is re-thrown when `cachedFn` is called with those same arguments.
- `cache` is for use in [Server Components](/reference/rsc/server-components) only.

---

## Usage {/*usage*/}

### Cache an expensive computation {/*cache-expensive-computation*/}

Use `cache` to skip duplicate work.

```js [[1, 7, "getUserMetrics(user)"],[2, 13, "getUserMetrics(user)"]]
import {cache} from 'react';
import calculateUserMetrics from 'lib/user';

const getUserMetrics = cache(calculateUserMetrics);

function Profile({user}) {
  const metrics = getUserMetrics(user);
  // ...
}

function TeamReport({users}) {
  for (let user in users) {
    const metrics = getUserMetrics(user);
    // ...
  }
  // ...
}
```

If the same `user` object is rendered in both `Profile` and `TeamReport`, the two components can share work and only call `calculateUserMetrics` once for that `user`.

Assume `Profile` is rendered first. It will call `getUserMetrics`, and check if there is a cached result. Since it is the first time `getUserMetrics` is called with that `user`, there will be a cache miss. `getUserMetrics` will then call `calculateUserMetrics` with that `user` and write the result to cache.

When `TeamReport` renders its list of `users` and reaches the same `user` object, it will call `getUserMetrics` and read the result from cache.

If `calculateUserMetrics` can be aborted by passing an [`AbortSignal`](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal), you can use [`cacheSignal()`](/reference/react/cacheSignal) to cancel the expensive computation if React has finished rendering. `calculateUserMetrics` may already handle cancellation internally by using `cacheSignal` directly.

> **Pitfall: Calling different memoized functions will read from different caches. {/*pitfall-different-memoized-functions*/}**
>
> To access the same cache, components must call the same memoized function.
> 
> ```js [[1, 7, "getWeekReport"], [1, 7, "cache(calculateWeekReport)"], [1, 8, "getWeekReport"]]
> // Temperature.js
> import {cache} from 'react';
> import {calculateWeekReport} from './report';
> 
> export function Temperature({cityData}) {
>   // 🚩 Wrong: Calling `cache` in component creates new `getWeekReport` for each render
>   const getWeekReport = cache(calculateWeekReport);
>   const report = getWeekReport(cityData);
>   // ...
> }
> ```
> 
> ```js [[2, 6, "getWeekReport"], [2, 6, "cache(calculateWeekReport)"], [2, 9, "getWeekReport"]]
> // Precipitation.js
> import {cache} from 'react';
> import {calculateWeekReport} from './report';
> 
> // 🚩 Wrong: `getWeekReport` is only accessible for `Precipitation` component.
> const getWeekReport = cache(calculateWeekReport);
> 
> export function Precipitation({cityData}) {
>   const report = getWeekReport(cityData);
>   // ...
> }
> ```
> 
> In the above example, `Precipitation` and `Temperature` each call `cache` to create a new memoized function with their own cache look-up. If both components render for the same `cityData`, they will do duplicate work to call `calculateWeekReport`.
> 
> In addition, `Temperature` creates a new memoized function each time the component is rendered which doesn't allow for any cache sharing.
> 
> To maximize cache hits and reduce work, the two components should call the same memoized function to access the same cache. Instead, define the memoized function in a dedicated module that can be [`import`-ed](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import) across components.
> 
> ```js [[3, 5, "export default cache(calculateWeekReport)"]]
> // getWeekReport.js
> import {cache} from 'react';
> import {calculateWeekReport} from './report';
> 
> export default cache(calculateWeekReport);
> ```
> 
> ```js [[3, 2, "getWeekReport", 0], [3, 5, "getWeekReport"]]
> // Temperature.js
> import getWeekReport from './getWeekReport';
> 
> export default function Temperature({cityData}) {
> 	const report = getWeekReport(cityData);
>   // ...
> }
> ```
> 
> ```js [[3, 2, "getWeekReport", 0], [3, 5, "getWeekReport"]]
> // Precipitation.js
> import getWeekReport from './getWeekReport';
> 
> export default function Precipitation({cityData}) {
>   const report = getWeekReport(cityData);
>   // ...
> }
> ```
> Here, both components call the same memoized function exported from `./getWeekReport.js` to read and write to the same cache.


### Share a snapshot of data {/*take-and-share-snapshot-of-data*/}

To share a snapshot of data between components, call `cache` with a data-fetching function like `fetch`. When multiple components make the same data fetch, only one request is made and the data returned is cached and shared across components. All components refer to the same snapshot of data across the server render.

```js [[1, 4, "city"], [1, 5, "fetchTemperature(city)"], [2, 4, "getTemperature"], [2, 9, "getTemperature"], [1, 9, "city"], [2, 14, "getTemperature"], [1, 14, "city"]]
import {cache} from 'react';
import {fetchTemperature} from './api.js';

const getTemperature = cache(async (city) => {
	return await fetchTemperature(city);
});

async function AnimatedWeatherCard({city}) {
	const temperature = await getTemperature(city);
	// ...
}

async function MinimalWeatherCard({city}) {
	const temperature = await getTemperature(city);
	// ...
}
```

If `AnimatedWeatherCard` and `MinimalWeatherCard` both render for the same city, they will receive the same snapshot of data from the memoized function.

If `AnimatedWeatherCard` and `MinimalWeatherCard` supply different city arguments to `getTemperature`, then `fetchTemperature` will be called twice and each call site will receive different data.

The city acts as a cache key.

> **Note:**
>
> 
> 
> Asynchronous rendering is only supported for Server Components.
> 
> ```js [[3, 1, "async"], [3, 2, "await"]]
> async function AnimatedWeatherCard({city}) {
> 	const temperature = await getTemperature(city);
> 	// ...
> }
> ```
> 
> To render components that use asynchronous data in Client Components, see [`use()` documentation](/reference/react/use).
> 
> 


### Preload data {/*preload-data*/}

By caching a long-running data fetch, you can kick off asynchronous work prior to rendering the component.

```jsx [[2, 6, "await getUser(id)"], [1, 17, "getUser(id)"]]
const getUser = cache(async (id) => {
  return await db.user.query(id);
});

async function Profile({id}) {
  const user = await getUser(id);
  return (
    <section>
      <img src={user.profilePic} />
      <h2>{user.name}</h2>
    </section>
  );
}

function Page({id}) {
  // ✅ Good: start fetching the user data
  getUser(id);
  // ... some computational work
  return (
    <>
      <Profile id={id} />
    </>
  );
}
```

When rendering `Page`, the component calls `getUser` but note that it doesn't use the returned data. This early `getUser` call kicks off the asynchronous database query that occurs while `Page` is doing other computational work and rendering children.

When rendering `Profile`, we call `getUser` again. If the initial `getUser` call has already returned and cached the user data, when `Profile` asks and waits for this data, it can simply read from the cache without requiring another remote procedure call. If the initial data request hasn't been completed, preloading data in this pattern reduces delay in data-fetching.

> **Deep Dive: Caching asynchronous work {/*caching-asynchronous-work*/}**
>
> When evaluating an [asynchronous function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function), you will receive a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) for that work. The promise holds the state of that work (_pending_, _fulfilled_, _failed_) and its eventual settled result.
> 
> In this example, the asynchronous function `fetchData` returns a promise that is awaiting the `fetch`.
> 
> ```js [[1, 1, "fetchData()"], [2, 8, "getData()"], [3, 10, "getData()"]]
> async function fetchData() {
>   return await fetch(`https://...`);
> }
> 
> const getData = cache(fetchData);
> 
> async function MyComponent() {
>   getData();
>   // ... some computational work
>   await getData();
>   // ...
> }
> ```
> 
> In calling `getData` the first time, the promise returned from `fetchData` is cached. Subsequent look-ups will then return the same promise.
> 
> Notice that the first `getData` call does not `await` whereas the second does. [`await`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await) is a JavaScript operator that will wait and return the settled result of the promise. The first `getData` call simply initiates the `fetch` to cache the promise for the second `getData` to look-up.
> 
> If by the second call the promise is still _pending_, then `await` will pause for the result. The optimization is that while we wait on the `fetch`, React can continue with computational work, thus reducing the wait time for the second call.
> 
> If the promise is already settled, either to an error or the _fulfilled_ result, `await` will return that value immediately. In both outcomes, there is a performance benefit.


> **Pitfall: Calling a memoized function outside of a component will not use the cache. {/*pitfall-memoized-call-outside-component*/}**
>
> ```jsx [[1, 3, "getUser"]]
> import {cache} from 'react';
> 
> const getUser = cache(async (userId) => {
>   return await db.user.query(userId);
> });
> 
> // 🚩 Wrong: Calling memoized function outside of component will not memoize.
> getUser('demo-id');
> 
> async function DemoProfile() {
>   // ✅ Good: `getUser` will memoize.
>   const user = await getUser('demo-id');
>   return <Profile user={user} />;
> }
> ```
> 
> React only provides cache access to the memoized function in a component. When calling `getUser` outside of a component, it will still evaluate the function but not read or update the cache.
> 
> This is because cache access is provided through a [context](/learn/passing-data-deeply-with-context) which is only accessible from a component.


> **Deep Dive: When should I use `cache`, [`memo`](/reference/react/memo), or [`useMemo`](/reference/react/useMemo)? {/*cache-memo-usememo*/}**
>
> All mentioned APIs offer memoization but the difference is what they're intended to memoize, who can access the cache, and when their cache is invalidated.
> 
> #### `useMemo` {/*deep-dive-use-memo*/}
> 
> In general, you should use [`useMemo`](/reference/react/useMemo) for caching an expensive computation in a Client Component across renders. As an example, to memoize a transformation of data within a component.
> 
> ```jsx {expectedErrors: {'react-compiler': [4]}} {4}
> 'use client';
> 
> function WeatherReport({record}) {
>   const avgTemp = useMemo(() => calculateAvg(record), record);
>   // ...
> }
> 
> function App() {
>   const record = getRecord();
>   return (
>     <>
>       <WeatherReport record={record} />
>       <WeatherReport record={record} />
>     </>
>   );
> }
> ```
> In this example, `App` renders two `WeatherReport`s with the same record. Even though both components do the same work, they cannot share work. `useMemo`'s cache is only local to the component.
> 
> However, `useMemo` does ensure that if `App` re-renders and the `record` object doesn't change, each component instance would skip work and use the memoized value of `avgTemp`. `useMemo` will only cache the last computation of `avgTemp` with the given dependencies.
> 
> #### `cache` {/*deep-dive-cache*/}
> 
> In general, you should use `cache` in Server Components to memoize work that can be shared across components.
> 
> ```js [[1, 12, "<WeatherReport city={city} />"], [3, 13, "<WeatherReport city={city} />"], [2, 1, "cache(fetchReport)"]]
> const cachedFetchReport = cache(fetchReport);
> 
> function WeatherReport({city}) {
>   const report = cachedFetchReport(city);
>   // ...
> }
> 
> function App() {
>   const city = "Los Angeles";
>   return (
>     <>
>       <WeatherReport city={city} />
>       <WeatherReport city={city} />
>     </>
>   );
> }
> ```
> Re-writing the previous example to use `cache`, in this case the second instance of `WeatherReport` will be able to skip duplicate work and read from the same cache as the first `WeatherReport`. Another difference from the previous example is that `cache` is also recommended for memoizing data fetches, unlike `useMemo` which should only be used for computations.
> 
> At this time, `cache` should only be used in Server Components and the cache will be invalidated across server requests.
> 
> #### `memo` {/*deep-dive-memo*/}
> 
> You should use [`memo`](reference/react/memo) to prevent a component re-rendering if its props are unchanged.
> 
> ```js
> 'use client';
> 
> function WeatherReport({record}) {
>   const avgTemp = calculateAvg(record);
>   // ...
> }
> 
> const MemoWeatherReport = memo(WeatherReport);
> 
> function App() {
>   const record = getRecord();
>   return (
>     <>
>       <MemoWeatherReport record={record} />
>       <MemoWeatherReport record={record} />
>     </>
>   );
> }
> ```
> 
> In this example, both `MemoWeatherReport` components will call `calculateAvg` when first rendered. However, if `App` re-renders, with no changes to `record`, none of the props have changed and `MemoWeatherReport` will not re-render.
> 
> Compared to `useMemo`, `memo` memoizes the component render based on props vs. specific computations. Similar to `useMemo`, the memoized component only caches the last render with the last prop values. Once the props change, the cache invalidates and the component re-renders.


---

## Troubleshooting {/*troubleshooting*/}

### My memoized function still runs even though I've called it with the same arguments {/*memoized-function-still-runs*/}

See prior mentioned pitfalls
* [Calling different memoized functions will read from different caches.](#pitfall-different-memoized-functions)
* [Calling a memoized function outside of a component will not use the cache.](#pitfall-memoized-call-outside-component)

If none of the above apply, it may be a problem with how React checks if something exists in cache.

If your arguments are not [primitives](https://developer.mozilla.org/en-US/docs/Glossary/Primitive) (ex. objects, functions, arrays), ensure you're passing the same object reference.

When calling a memoized function, React will look up the input arguments to see if a result is already cached. React will use shallow equality of the arguments to determine if there is a cache hit.

```js
import {cache} from 'react';

const calculateNorm = cache((vector) => {
  // ...
});

function MapMarker(props) {
  // 🚩 Wrong: props is an object that changes every render.
  const length = calculateNorm(props);
  // ...
}

function App() {
  return (
    <>
      <MapMarker x={10} y={10} z={10} />
      <MapMarker x={10} y={10} z={10} />
    </>
  );
}
```

In this case the two `MapMarker`s look like they're doing the same work and calling `calculateNorm` with the same value of `{x: 10, y: 10, z:10}`. Even though the objects contain the same values, they are not the same object reference as each component creates its own `props` object.

React will call [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) on the input to verify if there is a cache hit.

```js {3,9}
import {cache} from 'react';

const calculateNorm = cache((x, y, z) => {
  // ...
});

function MapMarker(props) {
  // ✅ Good: Pass primitives to memoized function
  const length = calculateNorm(props.x, props.y, props.z);
  // ...
}

function App() {
  return (
    <>
      <MapMarker x={10} y={10} z={10} />
      <MapMarker x={10} y={10} z={10} />
    </>
  );
}
```

One way to address this could be to pass the vector dimensions to `calculateNorm`. This works because the dimensions themselves are primitives.

Another solution may be to pass the vector object itself as a prop to the component. We'll need to pass the same object to both component instances.

```js {3,9,14}
import {cache} from 'react';

const calculateNorm = cache((vector) => {
  // ...
});

function MapMarker(props) {
  // ✅ Good: Pass the same `vector` object
  const length = calculateNorm(props.vector);
  // ...
}

function App() {
  const vector = [10, 10, 10];
  return (
    <>
      <MapMarker vector={vector} />
      <MapMarker vector={vector} />
    </>
  );
}
```


# Captureownerstack

`captureOwnerStack` reads the current Owner Stack in development and returns it as a string if available.

```js
const stack = captureOwnerStack();
```

<InlineToc />

---

## Reference {/*reference*/}

### `captureOwnerStack()` {/*captureownerstack*/}

Call `captureOwnerStack` to get the current Owner Stack.

```js {5,5}
import * as React from 'react';

function Component() {
  if (process.env.NODE_ENV !== 'production') {
    const ownerStack = React.captureOwnerStack();
    console.log(ownerStack);
  }
}
```

#### Parameters {/*parameters*/}

`captureOwnerStack` does not take any parameters.

#### Returns {/*returns*/}

`captureOwnerStack` returns `string | null`.

Owner Stacks are available in
- Component render
- Effects (e.g. `useEffect`)
- React's event handlers (e.g. `<button onClick={...} />`)
- React error handlers ([React Root options](/reference/react-dom/client/createRoot#parameters) `onCaughtError`, `onRecoverableError`, and `onUncaughtError`)

If no Owner Stack is available, `null` is returned (see [Troubleshooting: The Owner Stack is `null`](#the-owner-stack-is-null)).

#### Caveats {/*caveats*/}

- Owner Stacks are only available in development. `captureOwnerStack` will always return `null` outside of development.

> **Deep Dive: Owner Stack vs Component Stack {/*owner-stack-vs-component-stack*/}**
>
> The Owner Stack is different from the Component Stack available in React error handlers like [`errorInfo.componentStack` in `onUncaughtError`](/reference/react-dom/client/hydrateRoot#error-logging-in-production).
> 
> For example, consider the following code:
> 
> [Interactive example removed — see react.dev for live demo]
> 
> 
> `SubComponent` would throw an error.
> The Component Stack of that error would be
> 
> ```
> at SubComponent
> at fieldset
> at Component
> at main
> at React.Suspense
> at App
> ```
> 
> However, the Owner Stack would only read
> 
> ```
> at Component
> ```
> 
> Neither `App` nor the DOM components (e.g. `fieldset`) are considered Owners in this Stack since they didn't contribute to "creating" the node containing `SubComponent`. `App` and DOM components only forwarded the node. `App` just rendered the `children` node as opposed to `Component` which created a node containing `SubComponent` via `<SubComponent />`.
> 
> Neither `Navigation` nor `legend` are in the stack at all since it's only a sibling to a node containing `<SubComponent />`.
> 
> `SubComponent` is omitted because it's already part of the callstack.


## Usage {/*usage*/}

### Enhance a custom error overlay {/*enhance-a-custom-error-overlay*/}

```js [[1, 5, "console.error"], [4, 7, "captureOwnerStack"]]
import { captureOwnerStack } from "react";
import { instrumentedConsoleError } from "./errorOverlay";

const originalConsoleError = console.error;
console.error = function patchedConsoleError(...args) {
  originalConsoleError.apply(console, args);
  const ownerStack = captureOwnerStack();
  onConsoleError({
    // Keep in mind that in a real application, console.error can be
    // called with multiple arguments which you should account for.
    consoleMessage: args[0],
    ownerStack,
  });
};
```

If you intercept `console.error` calls to highlight them in an error overlay, you can call `captureOwnerStack` to include the Owner Stack.

[Interactive example removed — see react.dev for live demo]


## Troubleshooting {/*troubleshooting*/}

### The Owner Stack is `null` {/*the-owner-stack-is-null*/}

The call of `captureOwnerStack` happened outside of a React controlled function e.g. in a `setTimeout` callback, after a `fetch` call or in a custom DOM event handler. During render, Effects, React event handlers, and React error handlers (e.g. `hydrateRoot#options.onCaughtError`) Owner Stacks should be available.

In the example below, clicking the button will log an empty Owner Stack because `captureOwnerStack` was called during a custom DOM event handler. The Owner Stack must be captured earlier e.g. by moving the call of `captureOwnerStack` into the Effect body.
[Interactive example removed — see react.dev for live demo]


### `captureOwnerStack` is not available {/*captureownerstack-is-not-available*/}

`captureOwnerStack` is only exported in development builds. It will be `undefined` in production builds. If `captureOwnerStack` is used in files that are bundled for production and development, you should conditionally access it from a namespace import.

```js
// Don't use named imports of `captureOwnerStack` in files that are bundled for development and production.
import {captureOwnerStack} from 'react';
// Use a namespace import instead and access `captureOwnerStack` conditionally.
import * as React from 'react';

if (process.env.NODE_ENV !== 'production') {
  const ownerStack = React.captureOwnerStack();
  console.log('Owner Stack', ownerStack);
}
```


# Fragment

`<Fragment>`, often used via `<>...</>` syntax, lets you group elements without a wrapper node. 

<Canary> Fragments can also accept refs, which enable interacting with underlying DOM nodes without adding wrapper elements. See reference and usage below.</Canary>

```js
<>
  <OneChild />
  <AnotherChild />
</>
```

<InlineToc />

---

## Reference {/*reference*/}

### `<Fragment>` {/*fragment*/}

Wrap elements in `<Fragment>` to group them together in situations where you need a single element. Grouping elements in `Fragment` has no effect on the resulting DOM; it is the same as if the elements were not grouped. The empty JSX tag `<></>` is shorthand for `<Fragment></Fragment>` in most cases.

#### Props {/*props*/}

- **optional** `key`: Fragments declared with the explicit `<Fragment>` syntax may have [keys.](/learn/rendering-lists#keeping-list-items-in-order-with-key)
- <CanaryBadge />  **optional** `ref`: A ref object (e.g. from [`useRef`](/reference/react/useRef)) or [callback function](/reference/react-dom/components/common#ref-callback). React provides a `FragmentInstance` as the ref value that implements methods for interacting with the DOM nodes wrapped by the Fragment.

### <CanaryBadge /> FragmentInstance {/*fragmentinstance*/}

When you pass a ref to a fragment, React provides a `FragmentInstance` object with methods for interacting with the DOM nodes wrapped by the fragment:

**Event handling methods:**
- `addEventListener(type, listener, options?)`: Adds an event listener to all first-level DOM children of the Fragment.
- `removeEventListener(type, listener, options?)`: Removes an event listener from all first-level DOM children of the Fragment.
- `dispatchEvent(event)`: Dispatches an event to a virtual child of the Fragment to call any added listeners and can bubble to the DOM parent.

**Layout methods:**
- `compareDocumentPosition(otherNode)`: Compares the document position of the Fragment with another node.
  - If the Fragment has children, the native `compareDocumentPosition` value is returned. 
  - Empty Fragments will attempt to compare positioning within the React tree and include `Node.DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC`.
  - Elements that have a different relationship in the React tree and DOM tree due to portaling or other insertions are `Node.DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC`.
- `getClientRects()`: Returns a flat array of `DOMRect` objects representing the bounding rectangles of all children.
- `getRootNode()`: Returns the root node containing the Fragment's parent DOM node.

**Focus management methods:**
- `focus(options?)`: Focuses the first focusable DOM node in the Fragment. Focus is attempted on nested children depth-first.
- `focusLast(options?)`: Focuses the last focusable DOM node in the Fragment. Focus is attempted on nested children depth-first.
- `blur()`: Removes focus if `document.activeElement` is within the Fragment.

**Observer methods:**
- `observeUsing(observer)`: Starts observing the Fragment's DOM children with an IntersectionObserver or ResizeObserver.
- `unobserveUsing(observer)`: Stops observing the Fragment's DOM children with the specified observer.

#### Caveats {/*caveats*/}

- If you want to pass `key` to a Fragment, you can't use the `<>...</>` syntax. You have to explicitly import `Fragment` from `'react'` and render `<Fragment key={yourKey}>...</Fragment>`.

- React does not [reset state](/learn/preserving-and-resetting-state) when you go from rendering `<><Child /></>` to `[<Child />]` or back, or when you go from rendering `<><Child /></>` to `<Child />` and back. This only works a single level deep: for example, going from `<><><Child /></></>` to `<Child />` resets the state. See the precise semantics [here.](https://gist.github.com/clemmy/b3ef00f9507909429d8aa0d3ee4f986b)

- <CanaryBadge /> If you want to pass `ref` to a Fragment, you can't use the `<>...</>` syntax. You have to explicitly import `Fragment` from `'react'` and render `<Fragment ref={yourRef}>...</Fragment>`.

---

## Usage {/*usage*/}

### Returning multiple elements {/*returning-multiple-elements*/}

Use `Fragment`, or the equivalent `<>...</>` syntax, to group multiple elements together. You can use it to put multiple elements in any place where a single element can go. For example, a component can only return one element, but by using a Fragment you can group multiple elements together and then return them as a group:

```js {3,6}
function Post() {
  return (
    <>
      <PostTitle />
      <PostBody />
    </>
  );
}
```

Fragments are useful because grouping elements with a Fragment has no effect on layout or styles, unlike if you wrapped the elements in another container like a DOM element. If you inspect this example with the browser tools, you'll see that all `<h1>` and `<article>` DOM nodes appear as siblings without wrappers around them:

[Interactive example removed — see react.dev for live demo]


> **Deep Dive: How to write a Fragment without the special syntax? {/*how-to-write-a-fragment-without-the-special-syntax*/}**
>
> The example above is equivalent to importing `Fragment` from React:
> 
> ```js {1,5,8}
> import { Fragment } from 'react';
> 
> function Post() {
>   return (
>     <Fragment>
>       <PostTitle />
>       <PostBody />
>     </Fragment>
>   );
> }
> ```
> 
> Usually you won't need this unless you need to [pass a `key` to your `Fragment`.](#rendering-a-list-of-fragments)


---

### Assigning multiple elements to a variable {/*assigning-multiple-elements-to-a-variable*/}

Like any other element, you can assign Fragment elements to variables, pass them as props, and so on:

```js
function CloseDialog() {
  const buttons = (
    <>
      <OKButton />
      <CancelButton />
    </>
  );
  return (
    <AlertDialog buttons={buttons}>
      Are you sure you want to leave this page?
    </AlertDialog>
  );
}
```

---

### Grouping elements with text {/*grouping-elements-with-text*/}

You can use `Fragment` to group text together with components:

```js
function DateRangePicker({ start, end }) {
  return (
    <>
      From
      <DatePicker date={start} />
      to
      <DatePicker date={end} />
    </>
  );
}
```

---

### Rendering a list of Fragments {/*rendering-a-list-of-fragments*/}

Here's a situation where you need to write `Fragment` explicitly instead of using the `<></>` syntax. When you [render multiple elements in a loop](/learn/rendering-lists), you need to assign a `key` to each element. If the elements within the loop are Fragments, you need to use the normal JSX element syntax in order to provide the `key` attribute:

```js {3,6}
function Blog() {
  return posts.map(post =>
    <Fragment key={post.id}>
      <PostTitle title={post.title} />
      <PostBody body={post.body} />
    </Fragment>
  );
}
```

You can inspect the DOM to verify that there are no wrapper elements around the Fragment children:

[Interactive example removed — see react.dev for live demo]


---

### <CanaryBadge /> Using Fragment refs for DOM interaction {/*using-fragment-refs-for-dom-interaction*/}

Fragment refs allow you to interact with the DOM nodes wrapped by a Fragment without adding extra wrapper elements. This is useful for event handling, visibility tracking, focus management, and replacing deprecated patterns like `ReactDOM.findDOMNode()`.

```js
import { Fragment } from 'react';

function ClickableFragment({ children, onClick }) {
  return (
    <Fragment ref={fragmentInstance => {
      fragmentInstance.addEventListener('click', handleClick);
      return () => fragmentInstance.removeEventListener('click', handleClick);
    }}>
      {children}
    </Fragment>
  );
}
```
---

### <CanaryBadge /> Tracking visibility with Fragment refs {/*tracking-visibility-with-fragment-refs*/}

Fragment refs are useful for visibility tracking and intersection observation. This enables you to monitor when content becomes visible without requiring the child Components to expose refs:

```js {19,21,31-34}
import { Fragment, useRef, useLayoutEffect } from 'react';

function VisibilityObserverFragment({ threshold = 0.5, onVisibilityChange, children }) {
  const fragmentRef = useRef(null);

  useLayoutEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        onVisibilityChange(entries.some(entry => entry.isIntersecting))
      },
      { threshold }
    );
    
    fragmentRef.current.observeUsing(observer);
    return () => fragmentRef.current.unobserveUsing(observer);
  }, [threshold, onVisibilityChange]);

  return (
    <Fragment ref={fragmentRef}>
      {children}
    </Fragment>
  );
}

function MyComponent() {
  const handleVisibilityChange = (isVisible) => {
    console.log('Component is', isVisible ? 'visible' : 'hidden');
  };

  return (
    <VisibilityObserverFragment onVisibilityChange={handleVisibilityChange}>
      <SomeThirdPartyComponent />
      <AnotherComponent />
    </VisibilityObserverFragment>
  );
}
```

This pattern is an alternative to Effect-based visibility logging, which is an anti-pattern in most cases. Relying on Effects alone does not guarantee that the rendered Component is observable by the user.

---

### <CanaryBadge /> Focus management with Fragment refs {/*focus-management-with-fragment-refs*/}

Fragment refs provide focus management methods that work across all DOM nodes within the Fragment:

```js
import { Fragment, useRef } from 'react';

function FocusFragment({ children }) {
  return (
    <Fragment ref={(fragmentInstance) => fragmentInstance?.focus()}>
      {children}
    </Fragment>
  );
}
```

The `focus()` method focuses the first focusable element within the Fragment, while `focusLast()` focuses the last focusable element.


# Act

`act` is a test helper to apply pending React updates before making assertions.

```js
await act(async actFn)
```

To prepare a component for assertions, wrap the code rendering it and performing updates inside an `await act()` call. This makes your test run closer to how React works in the browser.

> **Note:**
>
> 
> You might find using `act()` directly a bit too verbose. To avoid some of the boilerplate, you could use a library like [React Testing Library](https://testing-library.com/docs/react-testing-library/intro), whose helpers are wrapped with `act()`.
> 



<InlineToc />

---

## Reference {/*reference*/}

### `await act(async actFn)` {/*await-act-async-actfn*/}

When writing UI tests, tasks like rendering, user events, or data fetching can be considered as “units” of interaction with a user interface. React provides a helper called `act()` that makes sure all updates related to these “units” have been processed and applied to the DOM before you make any assertions.

The name `act` comes from the [Arrange-Act-Assert](https://wiki.c2.com/?ArrangeActAssert) pattern.

```js {2,4}
it ('renders with button disabled', async () => {
  await act(async () => {
    root.render(<TestComponent />)
  });
  expect(container.querySelector('button')).toBeDisabled();
});
```

> **Note:**
>
> 
> 
> We recommend using `act` with `await` and an `async` function. Although the sync version works in many cases, it doesn't work in all cases and due to the way React schedules updates internally, it's difficult to predict when you can use the sync version.
> 
> We will deprecate and remove the sync version in the future.
> 
> 


#### Parameters {/*parameters*/}

* `async actFn`: An async function wrapping renders or interactions for components being tested. Any updates triggered within the `actFn`, are added to an internal act queue, which are then flushed together to process and apply any changes to the DOM. Since it is async, React will also run any code that crosses an async boundary, and flush any updates scheduled.

#### Returns {/*returns*/}

`act` does not return anything.

## Usage {/*usage*/}

When testing a component, you can use `act` to make assertions about its output.

For example, let’s say we have this `Counter` component, the usage examples below show how to test it:

```js
function Counter() {
  const [count, setCount] = useState(0);
  const handleClick = () => {
    setCount(prev => prev + 1);
  }

  useEffect(() => {
    document.title = `You clicked ${count} times`;
  }, [count]);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={handleClick}>
        Click me
      </button>
    </div>
  )
}
```

### Rendering components in tests {/*rendering-components-in-tests*/}

To test the render output of a component, wrap the render inside `act()`:

```js  {10,12}
import {act} from 'react';
import ReactDOMClient from 'react-dom/client';
import Counter from './Counter';

it('can render and update a counter', async () => {
  container = document.createElement('div');
  document.body.appendChild(container);
  
  // ✅ Render the component inside act().
  await act(() => {
    ReactDOMClient.createRoot(container).render(<Counter />);
  });
  
  const button = container.querySelector('button');
  const label = container.querySelector('p');
  expect(label.textContent).toBe('You clicked 0 times');
  expect(document.title).toBe('You clicked 0 times');
});
```

Here, we create a container, append it to the document, and render the `Counter` component inside `act()`. This ensures that the component is rendered and its effects are applied before making assertions.

Using `act` ensures that all updates have been applied before we make assertions.

### Dispatching events in tests {/*dispatching-events-in-tests*/}

To test events, wrap the event dispatch inside `act()`:

```js {14,16}
import {act} from 'react';
import ReactDOMClient from 'react-dom/client';
import Counter from './Counter';

it.only('can render and update a counter', async () => {
  const container = document.createElement('div');
  document.body.appendChild(container);
  
  await act( async () => {
    ReactDOMClient.createRoot(container).render(<Counter />);
  });
  
  // ✅ Dispatch the event inside act().
  await act(async () => {
    button.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });

  const button = container.querySelector('button');
  const label = container.querySelector('p');
  expect(label.textContent).toBe('You clicked 1 times');
  expect(document.title).toBe('You clicked 1 times');
});
```

Here, we render the component with `act`, and then dispatch the event inside another `act()`. This ensures that all updates from the event are applied before making assertions.

> **Pitfall:**
>
> 
> 
> Don’t forget that dispatching DOM events only works when the DOM container is added to the document. You can use a library like [React Testing Library](https://testing-library.com/docs/react-testing-library/intro) to reduce the boilerplate code.
> 
> 


## Troubleshooting {/*troubleshooting*/}

### I'm getting an error: "The current testing environment is not configured to support act(...)" {/*error-the-current-testing-environment-is-not-configured-to-support-act*/}

Using `act` requires setting `global.IS_REACT_ACT_ENVIRONMENT=true` in your test environment. This is to ensure that `act` is only used in the correct environment.

If you don't set the global, you will see an error like this:

<ConsoleBlock level="error">

Warning: The current testing environment is not configured to support act(...)

</ConsoleBlock>

To fix, add this to your global setup file for React tests:

```js
global.IS_REACT_ACT_ENVIRONMENT=true
```

> **Note:**
>
> 
> 
> In testing frameworks like [React Testing Library](https://testing-library.com/docs/react-testing-library/intro), `IS_REACT_ACT_ENVIRONMENT` is already set for you.
> 
> 

