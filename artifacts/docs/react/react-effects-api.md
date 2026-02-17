---
title: React Effects Api
source: react.dev
syllabus_weeks: [7]
topics: [useEffect, useLayoutEffect, useInsertionEffect, useEffectEvent, effects API, cleanup, dependencies]
---



# Useeffect

`useEffect` is a React Hook that lets you [synchronize a component with an external system.](/learn/synchronizing-with-effects)

```js
useEffect(setup, dependencies?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useEffect(setup, dependencies?)` {/*useeffect*/}

Call `useEffect` at the top level of your component to declare an Effect:

```js
import { useState, useEffect } from 'react';
import { createConnection } from './chat.js';

function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => {
      connection.disconnect();
    };
  }, [serverUrl, roomId]);
  // ...
}
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `setup`: The function with your Effect's logic. Your setup function may also optionally return a *cleanup* function. When your [component commits](/learn/render-and-commit#step-3-react-commits-changes-to-the-dom), React will run your setup function. After every commit with changed dependencies, React will first run the cleanup function (if you provided it) with the old values, and then run your setup function with the new values. After your component is removed from the DOM, React will run your cleanup function.
 
* **optional** `dependencies`: The list of all reactive values referenced inside of the `setup` code. Reactive values include props, state, and all the variables and functions declared directly inside your component body. If your linter is [configured for React](/learn/editor-setup#linting), it will verify that every reactive value is correctly specified as a dependency. The list of dependencies must have a constant number of items and be written inline like `[dep1, dep2, dep3]`. React will compare each dependency with its previous value using the [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison. If you omit this argument, your Effect will re-run after every commit of the component. [See the difference between passing an array of dependencies, an empty array, and no dependencies at all.](#examples-dependencies)

#### Returns {/*returns*/}

`useEffect` returns `undefined`.

#### Caveats {/*caveats*/}

* `useEffect` is a Hook, so you can only call it **at the top level of your component** or your own Hooks. You can't call it inside loops or conditions. If you need that, extract a new component and move the state into it.

* If you're **not trying to synchronize with some external system,** [you probably don't need an Effect.](/learn/you-might-not-need-an-effect)

* When Strict Mode is on, React will **run one extra development-only setup+cleanup cycle** before the first real setup. This is a stress-test that ensures that your cleanup logic "mirrors" your setup logic and that it stops or undoes whatever the setup is doing. If this causes a problem, [implement the cleanup function.](/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development)

* If some of your dependencies are objects or functions defined inside the component, there is a risk that they will **cause the Effect to re-run more often than needed.** To fix this, remove unnecessary [object](#removing-unnecessary-object-dependencies) and [function](#removing-unnecessary-function-dependencies) dependencies. You can also [extract state updates](#updating-state-based-on-previous-state-from-an-effect) and [non-reactive logic](#reading-the-latest-props-and-state-from-an-effect) outside of your Effect.

* If your Effect wasn't caused by an interaction (like a click), React will generally let the browser **paint the updated screen first before running your Effect.** If your Effect is doing something visual (for example, positioning a tooltip), and the delay is noticeable (for example, it flickers), replace `useEffect` with [`useLayoutEffect`.](/reference/react/useLayoutEffect)

* If your Effect is caused by an interaction (like a click), **React may run your Effect before the browser paints the updated screen**. This ensures that the result of the Effect can be observed by the event system. Usually, this works as expected. However, if you must defer the work until after paint, such as an `alert()`, you can use `setTimeout`. See [reactwg/react-18/128](https://github.com/reactwg/react-18/discussions/128) for more information.

* Even if your Effect was caused by an interaction (like a click), **React may allow the browser to repaint the screen before processing the state updates inside your Effect.** Usually, this works as expected. However, if you must block the browser from repainting the screen, you need to replace `useEffect` with [`useLayoutEffect`.](/reference/react/useLayoutEffect)

* Effects **only run on the client.** They don't run during server rendering.

---

## Usage {/*usage*/}

### Connecting to an external system {/*connecting-to-an-external-system*/}

Some components need to stay connected to the network, some browser API, or a third-party library, while they are displayed on the page. These systems aren't controlled by React, so they are called *external.*

To [connect your component to some external system,](/learn/synchronizing-with-effects) call `useEffect` at the top level of your component:

```js [[1, 8, "const connection = createConnection(serverUrl, roomId);"], [1, 9, "connection.connect();"], [2, 11, "connection.disconnect();"], [3, 13, "[serverUrl, roomId]"]]
import { useState, useEffect } from 'react';
import { createConnection } from './chat.js';

function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useEffect(() => {
  	const connection = createConnection(serverUrl, roomId);
    connection.connect();
  	return () => {
      connection.disconnect();
  	};
  }, [serverUrl, roomId]);
  // ...
}
```

You need to pass two arguments to `useEffect`:

1. A *setup function* with setup code that connects to that system.
   - It should return a *cleanup function* with cleanup code that disconnects from that system.
2. A list of dependencies including every value from your component used inside of those functions.

**React calls your setup and cleanup functions whenever it's necessary, which may happen multiple times:**

1. Your setup code runs when your component is added to the page *(mounts)*.
2. After every commit of your component where the dependencies have changed:
   - First, your cleanup code runs with the old props and state.
   - Then, your setup code runs with the new props and state.
3. Your cleanup code runs one final time after your component is removed from the page *(unmounts).*

**Let's illustrate this sequence for the example above.**  

When the `ChatRoom` component above gets added to the page, it will connect to the chat room with the initial `serverUrl` and `roomId`. If either `serverUrl` or `roomId` change as a result of a commit (say, if the user picks a different chat room in a dropdown), your Effect will *disconnect from the previous room, and connect to the next one.* When the `ChatRoom` component is removed from the page, your Effect will disconnect one last time.

**To [help you find bugs,](/learn/synchronizing-with-effects#step-3-add-cleanup-if-needed) in development React runs setup and cleanup one extra time before the setup.** This is a stress-test that verifies your Effect's logic is implemented correctly. If this causes visible issues, your cleanup function is missing some logic. The cleanup function should stop or undo whatever the setup function was doing. The rule of thumb is that the user shouldn't be able to distinguish between the setup being called once (as in production) and a *setup* → *cleanup* → *setup* sequence (as in development). [See common solutions.](/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development)

**Try to [write every Effect as an independent process](/learn/lifecycle-of-reactive-effects#each-effect-represents-a-separate-synchronization-process) and [think about a single setup/cleanup cycle at a time.](/learn/lifecycle-of-reactive-effects#thinking-from-the-effects-perspective)** It shouldn't matter whether your component is mounting, updating, or unmounting. When your cleanup logic correctly "mirrors" the setup logic, your Effect is resilient to running setup and cleanup as often as needed.

> **Note:**
>
> 
> 
> An Effect lets you [keep your component synchronized](/learn/synchronizing-with-effects) with some external system (like a chat service). Here, *external system* means any piece of code that's not controlled by React, such as:
> 
> * A timer managed with [`setInterval()`](https://developer.mozilla.org/en-US/docs/Web/API/setInterval) and [`clearInterval()`](https://developer.mozilla.org/en-US/docs/Web/API/clearInterval).
> * An event subscription using [`window.addEventListener()`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener) and [`window.removeEventListener()`](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/removeEventListener).
> * A third-party animation library with an API like `animation.start()` and `animation.reset()`.
> 
> **If you're not connecting to any external system, [you probably don't need an Effect.](/learn/you-might-not-need-an-effect)**
> 
> 


<Recipes titleText="Examples of connecting to an external system" titleId="examples-connecting">

#### Connecting to a chat server {/*connecting-to-a-chat-server*/}

In this example, the `ChatRoom` component uses an Effect to stay connected to an external system defined in `chat.js`. Press "Open chat" to make the `ChatRoom` component appear. This sandbox runs in development mode, so there is an extra connect-and-disconnect cycle, as [explained here.](/learn/synchronizing-with-effects#step-3-add-cleanup-if-needed) Try changing the `roomId` and `serverUrl` using the dropdown and the input, and see how the Effect re-connects to the chat. Press "Close chat" to see the Effect disconnect one last time.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Listening to a global browser event {/*listening-to-a-global-browser-event*/}

In this example, the external system is the browser DOM itself. Normally, you'd specify event listeners with JSX, but you can't listen to the global [`window`](https://developer.mozilla.org/en-US/docs/Web/API/Window) object this way. An Effect lets you connect to the `window` object and listen to its events. Listening to the `pointermove` event lets you track the cursor (or finger) position and update the red dot to move with it.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Triggering an animation {/*triggering-an-animation*/}

In this example, the external system is the animation library in `animation.js`. It provides a JavaScript class called `FadeInAnimation` that takes a DOM node as an argument and exposes `start()` and `stop()` methods to control the animation. This component [uses a ref](/learn/manipulating-the-dom-with-refs) to access the underlying DOM node. The Effect reads the DOM node from the ref and automatically starts the animation for that node when the component appears.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Controlling a modal dialog {/*controlling-a-modal-dialog*/}

In this example, the external system is the browser DOM. The `ModalDialog` component renders a [`<dialog>`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/dialog) element. It uses an Effect to synchronize the `isOpen` prop to the [`showModal()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/showModal) and [`close()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/close) method calls.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Tracking element visibility {/*tracking-element-visibility*/}

In this example, the external system is again the browser DOM. The `App` component displays a long list, then a `Box` component, and then another long list. Scroll the list down. Notice that when all of the `Box` component is fully visible in the viewport, the background color changes to black. To implement this, the `Box` component uses an Effect to manage an [`IntersectionObserver`](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API). This browser API notifies you when the DOM element is visible in the viewport.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Wrapping Effects in custom Hooks {/*wrapping-effects-in-custom-hooks*/}

Effects are an ["escape hatch":](/learn/escape-hatches) you use them when you need to "step outside React" and when there is no better built-in solution for your use case. If you find yourself often needing to manually write Effects, it's usually a sign that you need to extract some [custom Hooks](/learn/reusing-logic-with-custom-hooks) for common behaviors your components rely on.

For example, this `useChatRoom` custom Hook "hides" the logic of your Effect behind a more declarative API:

```js {1,11}
function useChatRoom({ serverUrl, roomId }) {
  useEffect(() => {
    const options = {
      serverUrl: serverUrl,
      roomId: roomId
    };
    const connection = createConnection(options);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId, serverUrl]);
}
```

Then you can use it from any component like this:

```js {4-7}
function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useChatRoom({
    roomId: roomId,
    serverUrl: serverUrl
  });
  // ...
```

There are also many excellent custom Hooks for every purpose available in the React ecosystem.

[Learn more about wrapping Effects in custom Hooks.](/learn/reusing-logic-with-custom-hooks)

<Recipes titleText="Examples of wrapping Effects in custom Hooks" titleId="examples-custom-hooks">

#### Custom `useChatRoom` Hook {/*custom-usechatroom-hook*/}

This example is identical to one of the [earlier examples,](#examples-connecting) but the logic is extracted to a custom Hook.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Custom `useWindowListener` Hook {/*custom-usewindowlistener-hook*/}

This example is identical to one of the [earlier examples,](#examples-connecting) but the logic is extracted to a custom Hook.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Custom `useIntersectionObserver` Hook {/*custom-useintersectionobserver-hook*/}

This example is identical to one of the [earlier examples,](#examples-connecting) but the logic is partially extracted to a custom Hook.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Controlling a non-React widget {/*controlling-a-non-react-widget*/}

Sometimes, you want to keep an external system synchronized to some prop or state of your component.

For example, if you have a third-party map widget or a video player component written without React, you can use an Effect to call methods on it that make its state match the current state of your React component. This Effect creates an instance of a `MapWidget` class defined in `map-widget.js`. When you change the `zoomLevel` prop of the `Map` component, the Effect calls the `setZoom()` on the class instance to keep it synchronized:

[Interactive example removed — see react.dev for live demo]


In this example, a cleanup function is not needed because the `MapWidget` class manages only the DOM node that was passed to it. After the `Map` React component is removed from the tree, both the DOM node and the `MapWidget` class instance will be automatically garbage-collected by the browser JavaScript engine.

---

### Fetching data with Effects {/*fetching-data-with-effects*/}

You can use an Effect to fetch data for your component. Note that [if you use a framework,](/learn/creating-a-react-app#full-stack-frameworks) using your framework's data fetching mechanism will be a lot more efficient than writing Effects manually.

If you want to fetch data from an Effect manually, your code might look like this:

```js
import { useState, useEffect } from 'react';
import { fetchBio } from './api.js';

export default function Page() {
  const [person, setPerson] = useState('Alice');
  const [bio, setBio] = useState(null);

  useEffect(() => {
    let ignore = false;
    setBio(null);
    fetchBio(person).then(result => {
      if (!ignore) {
        setBio(result);
      }
    });
    return () => {
      ignore = true;
    };
  }, [person]);

  // ...
```

Note the `ignore` variable which is initialized to `false`, and is set to `true` during cleanup. This ensures [your code doesn't suffer from "race conditions":](https://maxrozen.com/race-conditions-fetching-data-react-with-useeffect) network responses may arrive in a different order than you sent them.

[Interactive example removed — see react.dev for live demo]


You can also rewrite using the [`async` / `await`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function) syntax, but you still need to provide a cleanup function:

[Interactive example removed — see react.dev for live demo]


Writing data fetching directly in Effects gets repetitive and makes it difficult to add optimizations like caching and server rendering later. [It's easier to use a custom Hook--either your own or maintained by the community.](/learn/reusing-logic-with-custom-hooks#when-to-use-custom-hooks)

> **Deep Dive: What are good alternatives to data fetching in Effects? {/*what-are-good-alternatives-to-data-fetching-in-effects*/}**
>
> Writing `fetch` calls inside Effects is a [popular way to fetch data](https://www.robinwieruch.de/react-hooks-fetch-data/), especially in fully client-side apps. This is, however, a very manual approach and it has significant downsides:
> 
> - **Effects don't run on the server.** This means that the initial server-rendered HTML will only include a loading state with no data. The client computer will have to download all JavaScript and render your app only to discover that now it needs to load the data. This is not very efficient.
> - **Fetching directly in Effects makes it easy to create "network waterfalls".** You render the parent component, it fetches some data, renders the child components, and then they start fetching their data. If the network is not very fast, this is significantly slower than fetching all data in parallel.
> - **Fetching directly in Effects usually means you don't preload or cache data.** For example, if the component unmounts and then mounts again, it would have to fetch the data again.
> - **It's not very ergonomic.** There's quite a bit of boilerplate code involved when writing `fetch` calls in a way that doesn't suffer from bugs like [race conditions.](https://maxrozen.com/race-conditions-fetching-data-react-with-useeffect)
> 
> This list of downsides is not specific to React. It applies to fetching data on mount with any library. Like with routing, data fetching is not trivial to do well, so we recommend the following approaches:
> 
> - **If you use a [framework](/learn/creating-a-react-app#full-stack-frameworks), use its built-in data fetching mechanism.** Modern React frameworks have integrated data fetching mechanisms that are efficient and don't suffer from the above pitfalls.
> - **Otherwise, consider using or building a client-side cache.** Popular open source solutions include [TanStack Query](https://tanstack.com/query/latest/), [useSWR](https://swr.vercel.app/), and [React Router 6.4+.](https://beta.reactrouter.com/en/main/start/overview) You can build your own solution too, in which case you would use Effects under the hood but also add logic for deduplicating requests, caching responses, and avoiding network waterfalls (by preloading data or hoisting data requirements to routes).
> 
> You can continue fetching data directly in Effects if neither of these approaches suit you.


---

### Specifying reactive dependencies {/*specifying-reactive-dependencies*/}

**Notice that you can't "choose" the dependencies of your Effect.** Every reactive value used by your Effect's code must be declared as a dependency. Your Effect's dependency list is determined by the surrounding code:

```js [[2, 1, "roomId"], [2, 2, "serverUrl"], [2, 5, "serverUrl"], [2, 5, "roomId"], [2, 8, "serverUrl"], [2, 8, "roomId"]]
function ChatRoom({ roomId }) { // This is a reactive value
  const [serverUrl, setServerUrl] = useState('https://localhost:1234'); // This is a reactive value too

  useEffect(() => {
    const connection = createConnection(serverUrl, roomId); // This Effect reads these reactive values
    connection.connect();
    return () => connection.disconnect();
  }, [serverUrl, roomId]); // ✅ So you must specify them as dependencies of your Effect
  // ...
}
```

If either `serverUrl` or `roomId` change, your Effect will reconnect to the chat using the new values.

**[Reactive values](/learn/lifecycle-of-reactive-effects#effects-react-to-reactive-values) include props and all variables and functions declared directly inside of your component.** Since `roomId` and `serverUrl` are reactive values, you can't remove them from the dependencies. If you try to omit them and [your linter is correctly configured for React,](/learn/editor-setup#linting) the linter will flag this as a mistake you need to fix:

```js {8}
function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');
  
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => connection.disconnect();
  }, []); // 🔴 React Hook useEffect has missing dependencies: 'roomId' and 'serverUrl'
  // ...
}
```

**To remove a dependency, you need to ["prove" to the linter that it *doesn't need* to be a dependency.](/learn/removing-effect-dependencies#removing-unnecessary-dependencies)** For example, you can move `serverUrl` out of your component to prove that it's not reactive and won't change on re-renders:

```js {1,8}
const serverUrl = 'https://localhost:1234'; // Not a reactive value anymore

function ChatRoom({ roomId }) {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId]); // ✅ All dependencies declared
  // ...
}
```

Now that `serverUrl` is not a reactive value (and can't change on a re-render), it doesn't need to be a dependency. **If your Effect's code doesn't use any reactive values, its dependency list should be empty (`[]`):**

```js {1,2,9}
const serverUrl = 'https://localhost:1234'; // Not a reactive value anymore
const roomId = 'music'; // Not a reactive value anymore

function ChatRoom() {
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => connection.disconnect();
  }, []); // ✅ All dependencies declared
  // ...
}
```

[An Effect with empty dependencies](/learn/lifecycle-of-reactive-effects#what-an-effect-with-empty-dependencies-means) doesn't re-run when any of your component's props or state change.

> **Pitfall:**
>
> 
> 
> If you have an existing codebase, you might have some Effects that suppress the linter like this:
> 
> ```js {3-4}
> useEffect(() => {
>   // ...
>   // 🔴 Avoid suppressing the linter like this:
>   // eslint-ignore-next-line react-hooks/exhaustive-deps
> }, []);
> ```
> 
> **When dependencies don't match the code, there is a high risk of introducing bugs.** By suppressing the linter, you "lie" to React about the values your Effect depends on. [Instead, prove they're unnecessary.](/learn/removing-effect-dependencies#removing-unnecessary-dependencies)
> 
> 


<Recipes titleText="Examples of passing reactive dependencies" titleId="examples-dependencies">

#### Passing a dependency array {/*passing-a-dependency-array*/}

If you specify the dependencies, your Effect runs **after the initial commit _and_ after commits with changed dependencies.**

```js {3}
useEffect(() => {
  // ...
}, [a, b]); // Runs again if a or b are different
```

In the below example, `serverUrl` and `roomId` are [reactive values,](/learn/lifecycle-of-reactive-effects#effects-react-to-reactive-values) so they both must be specified as dependencies. As a result, selecting a different room in the dropdown or editing the server URL input causes the chat to re-connect. However, since `message` isn't used in the Effect (and so it isn't a dependency), editing the message doesn't re-connect to the chat.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Passing an empty dependency array {/*passing-an-empty-dependency-array*/}

If your Effect truly doesn't use any reactive values, it will only run **after the initial commit.**

```js {3}
useEffect(() => {
  // ...
}, []); // Does not run again (except once in development)
```

**Even with empty dependencies, setup and cleanup will [run one extra time in development](/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development) to help you find bugs.**


In this example, both `serverUrl` and `roomId` are hardcoded. Since they're declared outside the component, they are not reactive values, and so they aren't dependencies. The dependency list is empty, so the Effect doesn't re-run on re-renders.

[Interactive example removed — see react.dev for live demo]


<Solution />


#### Passing no dependency array at all {/*passing-no-dependency-array-at-all*/}

If you pass no dependency array at all, your Effect runs **after every single commit** of your component.

```js {3}
useEffect(() => {
  // ...
}); // Always runs again
```

In this example, the Effect re-runs when you change `serverUrl` and `roomId`, which is sensible. However, it *also* re-runs when you change the `message`, which is probably undesirable. This is why usually you'll specify the dependency array.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Updating state based on previous state from an Effect {/*updating-state-based-on-previous-state-from-an-effect*/}

When you want to update state based on previous state from an Effect, you might run into a problem:

```js {6,9}
function Counter() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCount(count + 1); // You want to increment the counter every second...
    }, 1000)
    return () => clearInterval(intervalId);
  }, [count]); // 🚩 ... but specifying `count` as a dependency always resets the interval.
  // ...
}
```

Since `count` is a reactive value, it must be specified in the list of dependencies. However, that causes the Effect to cleanup and setup again every time the `count` changes. This is not ideal. 

To fix this, [pass the `c => c + 1` state updater](/reference/react/useState#updating-state-based-on-the-previous-state) to `setCount`:

[Interactive example removed — see react.dev for live demo]


Now that you're passing `c => c + 1` instead of `count + 1`, [your Effect no longer needs to depend on `count`.](/learn/removing-effect-dependencies#are-you-reading-some-state-to-calculate-the-next-state) As a result of this fix, it won't need to cleanup and setup the interval again every time the `count` changes.

---


### Removing unnecessary object dependencies {/*removing-unnecessary-object-dependencies*/}

If your Effect depends on an object or a function created during rendering, it might run too often. For example, this Effect re-connects after every commit because the `options` object is [different for every render:](/learn/removing-effect-dependencies#does-some-reactive-value-change-unintentionally)

```js {6-9,12,15}
const serverUrl = 'https://localhost:1234';

function ChatRoom({ roomId }) {
  const [message, setMessage] = useState('');

  const options = { // 🚩 This object is created from scratch on every re-render
    serverUrl: serverUrl,
    roomId: roomId
  };

  useEffect(() => {
    const connection = createConnection(options); // It's used inside the Effect
    connection.connect();
    return () => connection.disconnect();
  }, [options]); // 🚩 As a result, these dependencies are always different on a commit
  // ...
```

Avoid using an object created during rendering as a dependency. Instead, create the object inside the Effect:

[Interactive example removed — see react.dev for live demo]


Now that you create the `options` object inside the Effect, the Effect itself only depends on the `roomId` string.

With this fix, typing into the input doesn't reconnect the chat. Unlike an object which gets re-created, a string like `roomId` doesn't change unless you set it to another value. [Read more about removing dependencies.](/learn/removing-effect-dependencies)

---

### Removing unnecessary function dependencies {/*removing-unnecessary-function-dependencies*/}

If your Effect depends on an object or a function created during rendering, it might run too often. For example, this Effect re-connects after every commit because the `createOptions` function is [different for every render:](/learn/removing-effect-dependencies#does-some-reactive-value-change-unintentionally)

```js {4-9,12,16}
function ChatRoom({ roomId }) {
  const [message, setMessage] = useState('');

  function createOptions() { // 🚩 This function is created from scratch on every re-render
    return {
      serverUrl: serverUrl,
      roomId: roomId
    };
  }

  useEffect(() => {
    const options = createOptions(); // It's used inside the Effect
    const connection = createConnection();
    connection.connect();
    return () => connection.disconnect();
  }, [createOptions]); // 🚩 As a result, these dependencies are always different on a commit
  // ...
```

By itself, creating a function from scratch on every re-render is not a problem. You don't need to optimize that. However, if you use it as a dependency of your Effect, it will cause your Effect to re-run after every commit.

Avoid using a function created during rendering as a dependency. Instead, declare it inside the Effect:

[Interactive example removed — see react.dev for live demo]


Now that you define the `createOptions` function inside the Effect, the Effect itself only depends on the `roomId` string. With this fix, typing into the input doesn't reconnect the chat. Unlike a function which gets re-created, a string like `roomId` doesn't change unless you set it to another value. [Read more about removing dependencies.](/learn/removing-effect-dependencies)

---

### Reading the latest props and state from an Effect {/*reading-the-latest-props-and-state-from-an-effect*/}

By default, when you read a reactive value from an Effect, you have to add it as a dependency. This ensures that your Effect "reacts" to every change of that value. For most dependencies, that's the behavior you want.

**However, sometimes you'll want to read the *latest* props and state from an Effect without "reacting" to them.** For example, imagine you want to log the number of the items in the shopping cart for every page visit:

```js {3}
function Page({ url, shoppingCart }) {
  useEffect(() => {
    logVisit(url, shoppingCart.length);
  }, [url, shoppingCart]); // ✅ All dependencies declared
  // ...
}
```

**What if you want to log a new page visit after every `url` change, but *not* if only the `shoppingCart` changes?** You can't exclude `shoppingCart` from dependencies without breaking the [reactivity rules.](#specifying-reactive-dependencies) However, you can express that you *don't want* a piece of code to "react" to changes even though it is called from inside an Effect. [Declare an *Effect Event*](/learn/separating-events-from-effects#declaring-an-effect-event) with the [`useEffectEvent`](/reference/react/useEffectEvent) Hook, and move the code reading `shoppingCart` inside of it:

```js {2-4,7,8}
function Page({ url, shoppingCart }) {
  const onVisit = useEffectEvent(visitedUrl => {
    logVisit(visitedUrl, shoppingCart.length)
  });

  useEffect(() => {
    onVisit(url);
  }, [url]); // ✅ All dependencies declared
  // ...
}
```

**Effect Events are not reactive and must always be omitted from dependencies of your Effect.** This is what lets you put non-reactive code (where you can read the latest value of some props and state) inside of them. By reading `shoppingCart` inside of `onVisit`, you ensure that `shoppingCart` won't re-run your Effect.

[Read more about how Effect Events let you separate reactive and non-reactive code.](/learn/separating-events-from-effects#reading-latest-props-and-state-with-effect-events)


---

### Displaying different content on the server and the client {/*displaying-different-content-on-the-server-and-the-client*/}

If your app uses server rendering (either [directly](/reference/react-dom/server) or via a [framework](/learn/creating-a-react-app#full-stack-frameworks)), your component will render in two different environments. On the server, it will render to produce the initial HTML. On the client, React will run the rendering code again so that it can attach your event handlers to that HTML. This is why, for [hydration](/reference/react-dom/client/hydrateRoot#hydrating-server-rendered-html) to work, your initial render output must be identical on the client and the server.

In rare cases, you might need to display different content on the client. For example, if your app reads some data from [`localStorage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage), it can't possibly do that on the server. Here is how you could implement this:


{/* TODO(@poteto) - investigate potential false positives in react compiler validation */}
```js {expectedErrors: {'react-compiler': [5]}}
function MyComponent() {
  const [didMount, setDidMount] = useState(false);

  useEffect(() => {
    setDidMount(true);
  }, []);

  if (didMount) {
    // ... return client-only JSX ...
  }  else {
    // ... return initial JSX ...
  }
}
```

While the app is loading, the user will see the initial render output. Then, when it's loaded and hydrated, your Effect will run and set `didMount` to `true`, triggering a re-render. This will switch to the client-only render output. Effects don't run on the server, so this is why `didMount` was `false` during the initial server render.

Use this pattern sparingly. Keep in mind that users with a slow connection will see the initial content for quite a bit of time--potentially, many seconds--so you don't want to make jarring changes to your component's appearance. In many cases, you can avoid the need for this by conditionally showing different things with CSS.

---

## Troubleshooting {/*troubleshooting*/}

### My Effect runs twice when the component mounts {/*my-effect-runs-twice-when-the-component-mounts*/}

When Strict Mode is on, in development, React runs setup and cleanup one extra time before the actual setup.

This is a stress-test that verifies your Effect’s logic is implemented correctly. If this causes visible issues, your cleanup function is missing some logic. The cleanup function should stop or undo whatever the setup function was doing. The rule of thumb is that the user shouldn’t be able to distinguish between the setup being called once (as in production) and a setup → cleanup → setup sequence (as in development).

Read more about [how this helps find bugs](/learn/synchronizing-with-effects#step-3-add-cleanup-if-needed) and [how to fix your logic.](/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development)

---

### My Effect runs after every re-render {/*my-effect-runs-after-every-re-render*/}

First, check that you haven't forgotten to specify the dependency array:

```js {3}
useEffect(() => {
  // ...
}); // 🚩 No dependency array: re-runs after every commit!
```

If you've specified the dependency array but your Effect still re-runs in a loop, it's because one of your dependencies is different on every re-render.

You can debug this problem by manually logging your dependencies to the console:

```js {5}
  useEffect(() => {
    // ..
  }, [serverUrl, roomId]);

  console.log([serverUrl, roomId]);
```

You can then right-click on the arrays from different re-renders in the console and select "Store as a global variable" for both of them. Assuming the first one got saved as `temp1` and the second one got saved as `temp2`, you can then use the browser console to check whether each dependency in both arrays is the same:

```js
Object.is(temp1[0], temp2[0]); // Is the first dependency the same between the arrays?
Object.is(temp1[1], temp2[1]); // Is the second dependency the same between the arrays?
Object.is(temp1[2], temp2[2]); // ... and so on for every dependency ...
```

When you find the dependency that is different on every re-render, you can usually fix it in one of these ways:

- [Updating state based on previous state from an Effect](#updating-state-based-on-previous-state-from-an-effect)
- [Removing unnecessary object dependencies](#removing-unnecessary-object-dependencies)
- [Removing unnecessary function dependencies](#removing-unnecessary-function-dependencies)
- [Reading the latest props and state from an Effect](#reading-the-latest-props-and-state-from-an-effect)

As a last resort (if these methods didn't help), wrap its creation with [`useMemo`](/reference/react/useMemo#memoizing-a-dependency-of-another-hook) or [`useCallback`](/reference/react/useCallback#preventing-an-effect-from-firing-too-often) (for functions).

---

### My Effect keeps re-running in an infinite cycle {/*my-effect-keeps-re-running-in-an-infinite-cycle*/}

If your Effect runs in an infinite cycle, these two things must be true:

- Your Effect is updating some state.
- That state leads to a re-render, which causes the Effect's dependencies to change.

Before you start fixing the problem, ask yourself whether your Effect is connecting to some external system (like DOM, network, a third-party widget, and so on). Why does your Effect need to set state? Does it synchronize with that external system? Or are you trying to manage your application's data flow with it?

If there is no external system, consider whether [removing the Effect altogether](/learn/you-might-not-need-an-effect) would simplify your logic.

If you're genuinely synchronizing with some external system, think about why and under what conditions your Effect should update the state. Has something changed that affects your component's visual output? If you need to keep track of some data that isn't used by rendering, a [ref](/reference/react/useRef#referencing-a-value-with-a-ref) (which doesn't trigger re-renders) might be more appropriate. Verify your Effect doesn't update the state (and trigger re-renders) more than needed.

Finally, if your Effect is updating the state at the right time, but there is still a loop, it's because that state update leads to one of the Effect's dependencies changing. [Read how to debug dependency changes.](/reference/react/useEffect#my-effect-runs-after-every-re-render)

---

### My cleanup logic runs even though my component didn't unmount {/*my-cleanup-logic-runs-even-though-my-component-didnt-unmount*/}

The cleanup function runs not only during unmount, but before every re-render with changed dependencies. Additionally, in development, React [runs setup+cleanup one extra time immediately after component mounts.](#my-effect-runs-twice-when-the-component-mounts)

If you have cleanup code without corresponding setup code, it's usually a code smell:

```js {2-5}
useEffect(() => {
  // 🔴 Avoid: Cleanup logic without corresponding setup logic
  return () => {
    doSomething();
  };
}, []);
```

Your cleanup logic should be "symmetrical" to the setup logic, and should stop or undo whatever setup did:

```js {2-3,5}
  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => {
      connection.disconnect();
    };
  }, [serverUrl, roomId]);
```

[Learn how the Effect lifecycle is different from the component's lifecycle.](/learn/lifecycle-of-reactive-effects#the-lifecycle-of-an-effect)

---

### My Effect does something visual, and I see a flicker before it runs {/*my-effect-does-something-visual-and-i-see-a-flicker-before-it-runs*/}

If your Effect must block the browser from [painting the screen,](/learn/render-and-commit#epilogue-browser-paint) replace `useEffect` with [`useLayoutEffect`](/reference/react/useLayoutEffect). Note that **this shouldn't be needed for the vast majority of Effects.** You'll only need this if it's crucial to run your Effect before the browser paint: for example, to measure and position a tooltip before the user sees it.


# Uselayouteffect

> **Pitfall:**
>
> 
> 
> `useLayoutEffect` can hurt performance. Prefer [`useEffect`](/reference/react/useEffect) when possible.
> 
> 


`useLayoutEffect` is a version of [`useEffect`](/reference/react/useEffect) that fires before the browser repaints the screen.

```js
useLayoutEffect(setup, dependencies?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useLayoutEffect(setup, dependencies?)` {/*useinsertioneffect*/}

Call `useLayoutEffect` to perform the layout measurements before the browser repaints the screen:

```js
import { useState, useRef, useLayoutEffect } from 'react';

function Tooltip() {
  const ref = useRef(null);
  const [tooltipHeight, setTooltipHeight] = useState(0);

  useLayoutEffect(() => {
    const { height } = ref.current.getBoundingClientRect();
    setTooltipHeight(height);
  }, []);
  // ...
```


[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `setup`: The function with your Effect's logic. Your setup function may also optionally return a *cleanup* function. Before your [component commits](/learn/render-and-commit#step-3-react-commits-changes-to-the-dom), React will run your setup function. After every commit with changed dependencies, React will first run the cleanup function (if you provided it) with the old values, and then run your setup function with the new values. Before your component is removed from the DOM, React will run your cleanup function.

* **optional** `dependencies`: The list of all reactive values referenced inside of the `setup` code. Reactive values include props, state, and all the variables and functions declared directly inside your component body. If your linter is [configured for React](/learn/editor-setup#linting), it will verify that every reactive value is correctly specified as a dependency. The list of dependencies must have a constant number of items and be written inline like `[dep1, dep2, dep3]`. React will compare each dependency with its previous value using the [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison. If you omit this argument, your Effect will re-run after every commit of the component.

#### Returns {/*returns*/}

`useLayoutEffect` returns `undefined`.

#### Caveats {/*caveats*/}

* `useLayoutEffect` is a Hook, so you can only call it **at the top level of your component** or your own Hooks. You can't call it inside loops or conditions. If you need that, extract a component and move the Effect there.

* When Strict Mode is on, React will **run one extra development-only setup+cleanup cycle** before the first real setup. This is a stress-test that ensures that your cleanup logic "mirrors" your setup logic and that it stops or undoes whatever the setup is doing. If this causes a problem, [implement the cleanup function.](/learn/synchronizing-with-effects#how-to-handle-the-effect-firing-twice-in-development)

* If some of your dependencies are objects or functions defined inside the component, there is a risk that they will **cause the Effect to re-run more often than needed.** To fix this, remove unnecessary [object](/reference/react/useEffect#removing-unnecessary-object-dependencies) and [function](/reference/react/useEffect#removing-unnecessary-function-dependencies) dependencies. You can also [extract state updates](/reference/react/useEffect#updating-state-based-on-previous-state-from-an-effect) and [non-reactive logic](/reference/react/useEffect#reading-the-latest-props-and-state-from-an-effect) outside of your Effect.

* Effects **only run on the client.** They don't run during server rendering.

* The code inside `useLayoutEffect` and all state updates scheduled from it **block the browser from repainting the screen.** When used excessively, this makes your app slow. When possible, prefer [`useEffect`.](/reference/react/useEffect)

* If you trigger a state update inside `useLayoutEffect`, React will execute all remaining Effects immediately including `useEffect`.

---

## Usage {/*usage*/}

### Measuring layout before the browser repaints the screen {/*measuring-layout-before-the-browser-repaints-the-screen*/}

Most components don't need to know their position and size on the screen to decide what to render. They only return some JSX. Then the browser calculates their *layout* (position and size) and repaints the screen.

Sometimes, that's not enough. Imagine a tooltip that appears next to some element on hover. If there's enough space, the tooltip should appear above the element, but if it doesn't fit, it should appear below. In order to render the tooltip at the right final position, you need to know its height (i.e. whether it fits at the top).

To do this, you need to render in two passes:

1. Render the tooltip anywhere (even with a wrong position).
2. Measure its height and decide where to place the tooltip.
3. Render the tooltip *again* in the correct place.

**All of this needs to happen before the browser repaints the screen.** You don't want the user to see the tooltip moving. Call `useLayoutEffect` to perform the layout measurements before the browser repaints the screen:

```js {5-8}
function Tooltip() {
  const ref = useRef(null);
  const [tooltipHeight, setTooltipHeight] = useState(0); // You don't know real height yet

  useLayoutEffect(() => {
    const { height } = ref.current.getBoundingClientRect();
    setTooltipHeight(height); // Re-render now that you know the real height
  }, []);

  // ...use tooltipHeight in the rendering logic below...
}
```

Here's how this works step by step:

1. `Tooltip` renders with the initial `tooltipHeight = 0`  (so the tooltip may be wrongly positioned).
2. React places it in the DOM and runs the code in `useLayoutEffect`.
3. Your `useLayoutEffect` [measures the height](https://developer.mozilla.org/en-US/docs/Web/API/Element/getBoundingClientRect) of the tooltip content and triggers an immediate re-render.
4. `Tooltip` renders again with the real `tooltipHeight` (so the tooltip is correctly positioned).
5. React updates it in the DOM, and the browser finally displays the tooltip.

Hover over the buttons below and see how the tooltip adjusts its position depending on whether it fits:

[Interactive example removed — see react.dev for live demo]


Notice that even though the `Tooltip` component has to render in two passes (first, with `tooltipHeight` initialized to `0` and then with the real measured height), you only see the final result. This is why you need `useLayoutEffect` instead of [`useEffect`](/reference/react/useEffect) for this example. Let's look at the difference in detail below.

<Recipes titleText="useLayoutEffect vs useEffect" titleId="examples">

#### `useLayoutEffect` blocks the browser from repainting {/*uselayouteffect-blocks-the-browser-from-repainting*/}

React guarantees that the code inside `useLayoutEffect` and any state updates scheduled inside it will be processed **before the browser repaints the screen.** This lets you render the tooltip, measure it, and re-render the tooltip again without the user noticing the first extra render. In other words, `useLayoutEffect` blocks the browser from painting.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### `useEffect` does not block the browser {/*useeffect-does-not-block-the-browser*/}

Here is the same example, but with [`useEffect`](/reference/react/useEffect) instead of `useLayoutEffect`. If you're on a slower device, you might notice that sometimes the tooltip "flickers" and you briefly see its initial position before the corrected position.

[Interactive example removed — see react.dev for live demo]


To make the bug easier to reproduce, this version adds an artificial delay during rendering. React will let the browser paint the screen before it processes the state update inside `useEffect`. As a result, the tooltip flickers:

[Interactive example removed — see react.dev for live demo]


Edit this example to `useLayoutEffect` and observe that it blocks the paint even if rendering is slowed down.

<Solution />

</Recipes>

> **Note:**
>
> 
> 
> Rendering in two passes and blocking the browser hurts performance. Try to avoid this when you can.
> 
> 


---

## Troubleshooting {/*troubleshooting*/}

### I'm getting an error: "`useLayoutEffect` does nothing on the server" {/*im-getting-an-error-uselayouteffect-does-nothing-on-the-server*/}

The purpose of `useLayoutEffect` is to let your component [use layout information for rendering:](#measuring-layout-before-the-browser-repaints-the-screen)

1. Render the initial content.
2. Measure the layout *before the browser repaints the screen.*
3. Render the final content using the layout information you've read.

When you or your framework uses [server rendering](/reference/react-dom/server), your React app renders to HTML on the server for the initial render. This lets you show the initial HTML before the JavaScript code loads.

The problem is that on the server, there is no layout information.

In the [earlier example](#measuring-layout-before-the-browser-repaints-the-screen), the `useLayoutEffect` call in the `Tooltip` component lets it position itself correctly (either above or below content) depending on the content height. If you tried to render `Tooltip` as a part of the initial server HTML, this would be impossible to determine. On the server, there is no layout yet! So, even if you rendered it on the server, its position would "jump" on the client after the JavaScript loads and runs.

Usually, components that rely on layout information don't need to render on the server anyway. For example, it probably doesn't make sense to show a `Tooltip` during the initial render. It is triggered by a client interaction.

However, if you're running into this problem, you have a few different options:

- Replace `useLayoutEffect` with [`useEffect`.](/reference/react/useEffect) This tells React that it's okay to display the initial render result without blocking the paint (because the original HTML will become visible before your Effect runs).

- Alternatively, [mark your component as client-only.](/reference/react/Suspense#providing-a-fallback-for-server-errors-and-client-only-content) This tells React to replace its content up to the closest [`<Suspense>`](/reference/react/Suspense) boundary with a loading fallback (for example, a spinner or a glimmer) during server rendering.

- Alternatively, you can render a component with `useLayoutEffect` only after hydration. Keep a boolean `isMounted` state that's initialized to `false`, and set it to `true` inside a `useEffect` call. Your rendering logic can then be like `return isMounted ? <RealContent /> : <FallbackContent />`. On the server and during the hydration, the user will see `FallbackContent` which should not call `useLayoutEffect`. Then React will replace it with `RealContent` which runs on the client only and can include `useLayoutEffect` calls.

- If you synchronize your component with an external data store and rely on `useLayoutEffect` for different reasons than measuring layout, consider [`useSyncExternalStore`](/reference/react/useSyncExternalStore) instead which [supports server rendering.](/reference/react/useSyncExternalStore#adding-support-for-server-rendering)


# Useinsertioneffect

> **Pitfall:**
>
> 
> 
> `useInsertionEffect` is for CSS-in-JS library authors. Unless you are working on a CSS-in-JS library and need a place to inject the styles, you probably want [`useEffect`](/reference/react/useEffect) or [`useLayoutEffect`](/reference/react/useLayoutEffect) instead.
> 
> 


`useInsertionEffect` allows inserting elements into the DOM before any layout Effects fire.

```js
useInsertionEffect(setup, dependencies?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useInsertionEffect(setup, dependencies?)` {/*useinsertioneffect*/}

Call `useInsertionEffect` to insert styles before any Effects fire that may need to read layout:

```js
import { useInsertionEffect } from 'react';

// Inside your CSS-in-JS library
function useCSS(rule) {
  useInsertionEffect(() => {
    // ... inject <style> tags here ...
  });
  return rule;
}
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `setup`: The function with your Effect's logic. Your setup function may also optionally return a *cleanup* function. When your component is added to the DOM, but before any layout Effects fire, React will run your setup function. After every re-render with changed dependencies, React will first run the cleanup function (if you provided it) with the old values, and then run your setup function with the new values. When your component is removed from the DOM, React will run your cleanup function.
 
* **optional** `dependencies`: The list of all reactive values referenced inside of the `setup` code. Reactive values include props, state, and all the variables and functions declared directly inside your component body. If your linter is [configured for React](/learn/editor-setup#linting), it will verify that every reactive value is correctly specified as a dependency. The list of dependencies must have a constant number of items and be written inline like `[dep1, dep2, dep3]`. React will compare each dependency with its previous value using the [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison algorithm. If you don't specify the dependencies at all, your Effect will re-run after every re-render of the component.

#### Returns {/*returns*/}

`useInsertionEffect` returns `undefined`.

#### Caveats {/*caveats*/}

* Effects only run on the client. They don't run during server rendering.
* You can't update state from inside `useInsertionEffect`.
* By the time `useInsertionEffect` runs, refs are not attached yet.
* `useInsertionEffect` may run either before or after the DOM has been updated. You shouldn't rely on the DOM being updated at any particular time.
* Unlike other types of Effects, which fire cleanup for every Effect and then setup for every Effect, `useInsertionEffect` will fire both cleanup and setup one component at a time. This results in an "interleaving" of the cleanup and setup functions.
---

## Usage {/*usage*/}

### Injecting dynamic styles from CSS-in-JS libraries {/*injecting-dynamic-styles-from-css-in-js-libraries*/}

Traditionally, you would style React components using plain CSS.

```js
// In your JS file:
<button className="success" />

// In your CSS file:
.success { color: green; }
```

Some teams prefer to author styles directly in JavaScript code instead of writing CSS files. This usually requires using a CSS-in-JS library or a tool. There are three common approaches to CSS-in-JS:

1. Static extraction to CSS files with a compiler
2. Inline styles, e.g. `<div style={{ opacity: 1 }}>`
3. Runtime injection of `<style>` tags

If you use CSS-in-JS, we recommend a combination of the first two approaches (CSS files for static styles, inline styles for dynamic styles). **We don't recommend runtime `<style>` tag injection for two reasons:**

1. Runtime injection forces the browser to recalculate the styles a lot more often.
2. Runtime injection can be very slow if it happens at the wrong time in the React lifecycle.

The first problem is not solvable, but `useInsertionEffect` helps you solve the second problem.

Call `useInsertionEffect` to insert the styles before any layout Effects fire:

```js {4-11}
// Inside your CSS-in-JS library
let isInserted = new Set();
function useCSS(rule) {
  useInsertionEffect(() => {
    // As explained earlier, we don't recommend runtime injection of <style> tags.
    // But if you have to do it, then it's important to do in useInsertionEffect.
    if (!isInserted.has(rule)) {
      isInserted.add(rule);
      document.head.appendChild(getStyleForRule(rule));
    }
  });
  return rule;
}

function Button() {
  const className = useCSS('...');
  return <div className={className} />;
}
```

Similarly to `useEffect`, `useInsertionEffect` does not run on the server. If you need to collect which CSS rules have been used on the server, you can do it during rendering:

```js {1,4-6}
let collectedRulesSet = new Set();

function useCSS(rule) {
  if (typeof window === 'undefined') {
    collectedRulesSet.add(rule);
  }
  useInsertionEffect(() => {
    // ...
  });
  return rule;
}
```

[Read more about upgrading CSS-in-JS libraries with runtime injection to `useInsertionEffect`.](https://github.com/reactwg/react-18/discussions/110)

> **Deep Dive: How is this better than injecting styles during rendering or useLayoutEffect? {/*how-is-this-better-than-injecting-styles-during-rendering-or-uselayouteffect*/}**
>
> If you insert styles during rendering and React is processing a [non-blocking update,](/reference/react/useTransition#perform-non-blocking-updates-with-actions) the browser will recalculate the styles every single frame while rendering a component tree, which can be **extremely slow.**
> 
> `useInsertionEffect` is better than inserting styles during [`useLayoutEffect`](/reference/react/useLayoutEffect) or [`useEffect`](/reference/react/useEffect) because it ensures that by the time other Effects run in your components, the `<style>` tags have already been inserted. Otherwise, layout calculations in regular Effects would be wrong due to outdated styles.



# Useeffectevent

`useEffectEvent` is a React Hook that lets you separate events from Effects.

```js
const onEvent = useEffectEvent(callback)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useEffectEvent(callback)` {/*useeffectevent*/}

Call `useEffectEvent` at the top level of your component to create an Effect Event.

```js {4,6}
import { useEffectEvent, useEffect } from 'react';

function ChatRoom({ roomId, theme }) {
  const onConnected = useEffectEvent(() => {
    showNotification('Connected!', theme);
  });
}
```

Effect Events are a part of your Effect logic, but they behave more like an event handler. They always “see” the latest values from render (like props and state) without re-synchronizing your Effect, so they're excluded from Effect dependencies. See [Separating Events from Effects](/learn/separating-events-from-effects#extracting-non-reactive-logic-out-of-effects) to learn more. 

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `callback`: A function containing the logic for your Effect Event. The function can accept any number of arguments and return any value. When you call the returned Effect Event function, the `callback` always accesses the latest committed values from render at the time of the call. 

#### Returns {/*returns*/}

`useEffectEvent` returns an Effect Event function with the same type signature as your `callback`. 

You can call this function inside `useEffect`, `useLayoutEffect`, `useInsertionEffect`, or from within other Effect Events in the same component.

#### Caveats {/*caveats*/}

* `useEffectEvent` is a Hook, so you can only call it **at the top level of your component** or your own Hooks. You can't call it inside loops or conditions. If you need that, extract a new component and move the Effect Event into it.
* Effect Events can only be called from inside Effects or other Effect Events. Do not call them during rendering or pass them to other components or Hooks. The [`eslint-plugin-react-hooks`](/reference/eslint-plugin-react-hooks) linter enforces this restriction.
* Do not use `useEffectEvent` to avoid specifying dependencies in your Effect's dependency array. This hides bugs and makes your code harder to understand. Only use it for logic that is genuinely an event fired from Effects.
* Effect Event functions do not have a stable identity. Their identity intentionally changes on every render.

> **Deep Dive: Why are Effect Events not stable? {/*why-are-effect-events-not-stable*/}**
>
> Unlike `set` functions from `useState` or refs, Effect Event functions do not have a stable identity. Their identity intentionally changes on every render:
> 
> ```js
> // 🔴 Wrong: including Effect Event in dependencies
> useEffect(() => {
>   onSomething();
> }, [onSomething]); // ESLint will warn about this
> ```
> 
> This is a deliberate design choice. Effect Events are meant to be called only from within Effects in the same component. Since you can only call them locally and cannot pass them to other components or include them in dependency arrays, a stable identity would serve no purpose, and would actually mask bugs.
> 
> The non-stable identity acts as a runtime assertion: if your code incorrectly depends on the function identity, you'll see the Effect re-running on every render, making the bug obvious.
> 
> This design reinforces that Effect Events conceptually belong to a particular effect, and are not a general purpose API to opt-out of reactivity.


---

## Usage {/*usage*/}


### Using an event in an Effect {/*using-an-event-in-an-effect*/}

Call `useEffectEvent` at the top level of your component to create an *Effect Event*:


```js [[1, 1, "onConnected"]]
const onConnected = useEffectEvent(() => {
  if (!muted) {
    showNotification('Connected!');
  }
});
```

`useEffectEvent` accepts an `event callback` and returns an Effect Event. The Effect Event is a function that can be called inside of Effects without re-connecting the Effect:

```js [[1, 3, "onConnected"]]
useEffect(() => {
  const connection = createConnection(roomId);
  connection.on('connected', onConnected);
  connection.connect();
  return () => {
    connection.disconnect();
  }
}, [roomId]);
```

Since `onConnected` is an Effect Event, `muted` and `onConnect` are not in the Effect dependencies.

> **Pitfall: Don't use Effect Events to skip dependencies {/*pitfall-skip-dependencies*/}**
>
> It might be tempting to use `useEffectEvent` to avoid listing dependencies that you think are "unnecessary." However, this hides bugs and makes your code harder to understand:
> 
> ```js
> // 🔴 Wrong: Using Effect Events to hide dependencies
> const logVisit = useEffectEvent(() => {
>   log(pageUrl);
> });
> 
> useEffect(() => {
>   logVisit()
> }, []); // Missing pageUrl means you miss logs
> ```
> 
> If a value should cause your Effect to re-run, keep it as a dependency. Only use Effect Events for logic that genuinely should not re-trigger your Effect.
> 
> See [Separating Events from Effects](/learn/separating-events-from-effects) to learn more.


---

### Using a timer with latest values {/*using-a-timer-with-latest-values*/}

When you use `setInterval` or `setTimeout` in an Effect, you often want to read the latest values from render without restarting the timer whenever those values change.

This counter increments `count` by the current `increment` value every second. The `onTick` Effect Event reads the latest `count` and `increment` without causing the interval to restart:

[Interactive example removed — see react.dev for live demo]


Try changing the increment value while the timer is running. The counter immediately uses the new increment value, but the timer keeps ticking smoothly without restarting.

---

### Using an event listener with latest values {/*using-an-event-listener-with-latest-values*/}

When you set up an event listener in an Effect, you often need to read the latest values from render in the callback. Without `useEffectEvent`, you would need to include the values in your dependencies, causing the listener to be removed and re-added on every change.

This example shows a dot that follows the cursor, but only when "Can move" is checked. The `onMove` Effect Event always reads the latest `canMove` value without re-running the Effect:

[Interactive example removed — see react.dev for live demo]


Toggle the checkbox and move your cursor. The dot responds immediately to the checkbox state, but the event listener is only set up once when the component mounts.

---

### Avoid reconnecting to external systems {/*showing-a-notification-without-reconnecting*/}

A common use case for `useEffectEvent` is when you want to do something in response to an Effect, but that "something" depends on a value you don't want to react to.

In this example, a chat component connects to a room and shows a notification when connected. The user can mute notifications with a checkbox. However, you don't want to reconnect to the chat room every time the user changes the settings:

[Interactive example removed — see react.dev for live demo]


Try switching rooms. The chat reconnects and shows a notification. Now mute the notifications. Since `muted` is read inside the Effect Event rather than the Effect, the chat stays connected.

---

### Using Effect Events in custom Hooks {/*using-effect-events-in-custom-hooks*/}

You can use `useEffectEvent` inside your own custom Hooks. This lets you create reusable Hooks that encapsulate Effects while keeping some values non-reactive:

[Interactive example removed — see react.dev for live demo]


In this example, `useInterval` is a custom Hook that sets up an interval. The `callback` passed to it is wrapped in an Effect Event, so the interval does not reset even if a new `callback` is passed in every render.

---

## Troubleshooting {/*troubleshooting*/}

### I'm getting an error: "A function wrapped in useEffectEvent can't be called during rendering" {/*cant-call-during-rendering*/}

This error means you're calling an Effect Event function during the render phase of your component. Effect Events can only be called from inside Effects or other Effect Events.

```js
function MyComponent({ data }) {
  const onLog = useEffectEvent(() => {
    console.log(data);
  });

  // 🔴 Wrong: calling during render
  onLog();

  // ✅ Correct: call from an Effect
  useEffect(() => {
    onLog();
  }, []);

  return <div>{data}</div>;
}
```

If you need to run logic during render, don't wrap it in `useEffectEvent`. Call the logic directly or move it into an Effect.

---

### I'm getting a lint error: "Functions returned from useEffectEvent must not be included in the dependency array" {/*effect-event-in-deps*/}

If you see a warning like "Functions returned from `useEffectEvent` must not be included in the dependency array", remove the Effect Event from your dependencies:

```js
const onSomething = useEffectEvent(() => {
  // ...
});

// 🔴 Wrong: Effect Event in dependencies
useEffect(() => {
  onSomething();
}, [onSomething]);

// ✅ Correct: no Effect Event in dependencies
useEffect(() => {
  onSomething();
}, []);
```

Effect Events are designed to be called from Effects without being listed as dependencies. The linter enforces this because the function identity is [intentionally not stable](#why-are-effect-events-not-stable). Including it would cause your Effect to re-run on every render.

---

### I'm getting a lint error: "... is a function created with useEffectEvent, and can only be called from Effects" {/*effect-event-called-outside-effect*/}

If you see a warning like "... is a function created with React Hook `useEffectEvent`, and can only be called from Effects and Effect Events", you're calling the function from the wrong place:

```js
const onSomething = useEffectEvent(() => {
  console.log(value);
});

// 🔴 Wrong: calling from event handler
function handleClick() {
  onSomething();
}

// 🔴 Wrong: passing to child component
return <Child onSomething={onSomething} />;

// ✅ Correct: calling from Effect
useEffect(() => {
  onSomething();
}, []);
```

Effect Events are specifically designed to be used in Effects local to the component they're defined in. If you need a callback for event handlers or to pass to children, use a regular function or `useCallback` instead.