---
title: React Custom Hooks
source: react.dev
syllabus_weeks: [7]
topics: [custom hooks, hook design, reusable logic, hook composition, useDebugValue]
---



# Reusing Logic With Custom Hooks

React comes with several built-in Hooks like `useState`, `useContext`, and `useEffect`. Sometimes, you'll wish that there was a Hook for some more specific purpose: for example, to fetch data, to keep track of whether the user is online, or to connect to a chat room. You might not find these Hooks in React, but you can create your own Hooks for your application's needs.

- What custom Hooks are, and how to write your own
- How to reuse logic between components
- How to name and structure your custom Hooks
- When and why to extract custom Hooks

## Custom Hooks: Sharing logic between components {/*custom-hooks-sharing-logic-between-components*/}

Imagine you're developing an app that heavily relies on the network (as most apps do). You want to warn the user if their network connection has accidentally gone off while they were using your app. How would you go about it? It seems like you'll need two things in your component:

1. A piece of state that tracks whether the network is online.
2. An Effect that subscribes to the global [`online`](https://developer.mozilla.org/en-US/docs/Web/API/Window/online_event) and [`offline`](https://developer.mozilla.org/en-US/docs/Web/API/Window/offline_event) events, and updates that state.

This will keep your component [synchronized](/learn/synchronizing-with-effects) with the network status. You might start with something like this:

[Interactive example removed — see react.dev for live demo]


Try turning your network on and off, and notice how this `StatusBar` updates in response to your actions.

Now imagine you *also* want to use the same logic in a different component. You want to implement a Save button that will become disabled and show "Reconnecting..." instead of "Save" while the network is off.

To start, you can copy and paste the `isOnline` state and the Effect into `SaveButton`:

[Interactive example removed — see react.dev for live demo]


Verify that, if you turn off the network, the button will change its appearance.

These two components work fine, but the duplication in logic between them is unfortunate. It seems like even though they have different *visual appearance,* you want to reuse the logic between them.

### Extracting your own custom Hook from a component {/*extracting-your-own-custom-hook-from-a-component*/}

Imagine for a moment that, similar to [`useState`](/reference/react/useState) and [`useEffect`](/reference/react/useEffect), there was a built-in `useOnlineStatus` Hook. Then both of these components could be simplified and you could remove the duplication between them:

```js {2,7}
function StatusBar() {
  const isOnline = useOnlineStatus();
  return <h1>{isOnline ? '✅ Online' : '❌ Disconnected'}</h1>;
}

function SaveButton() {
  const isOnline = useOnlineStatus();

  function handleSaveClick() {
    console.log('✅ Progress saved');
  }

  return (
    <button disabled={!isOnline} onClick={handleSaveClick}>
      {isOnline ? 'Save progress' : 'Reconnecting...'}
    </button>
  );
}
```

Although there is no such built-in Hook, you can write it yourself. Declare a function called `useOnlineStatus` and move all the duplicated code into it from the components you wrote earlier:

```js {2-16}
function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
    }
    function handleOffline() {
      setIsOnline(false);
    }
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);
  return isOnline;
}
```

At the end of the function, return `isOnline`. This lets your components read that value:

[Interactive example removed — see react.dev for live demo]


Verify that switching the network on and off updates both components.

Now your components don't have as much repetitive logic. **More importantly, the code inside them describes *what they want to do* (use the online status!) rather than *how to do it* (by subscribing to the browser events).**

When you extract logic into custom Hooks, you can hide the gnarly details of how you deal with some external system or a browser API. The code of your components expresses your intent, not the implementation.

### Hook names always start with `use` {/*hook-names-always-start-with-use*/}

React applications are built from components. Components are built from Hooks, whether built-in or custom. You'll likely often use custom Hooks created by others, but occasionally you might write one yourself!

You must follow these naming conventions:

1. **React component names must start with a capital letter,** like `StatusBar` and `SaveButton`. React components also need to return something that React knows how to display, like a piece of JSX.
2. **Hook names must start with `use` followed by a capital letter,** like [`useState`](/reference/react/useState) (built-in) or `useOnlineStatus` (custom, like earlier on the page). Hooks may return arbitrary values.

This convention guarantees that you can always look at a component and know where its state, Effects, and other React features might "hide". For example, if you see a `getColor()` function call inside your component, you can be sure that it can't possibly contain React state inside because its name doesn't start with `use`. However, a function call like `useOnlineStatus()` will most likely contain calls to other Hooks inside!

> **Note:**
>
> 
> 
> If your linter is [configured for React,](/learn/editor-setup#linting) it will enforce this naming convention. Scroll up to the sandbox above and rename `useOnlineStatus` to `getOnlineStatus`. Notice that the linter won't allow you to call `useState` or `useEffect` inside of it anymore. Only Hooks and components can call other Hooks!
> 
> 


> **Deep Dive: Should all functions called during rendering start with the use prefix? {/*should-all-functions-called-during-rendering-start-with-the-use-prefix*/}**
>
> No. Functions that don't *call* Hooks don't need to *be* Hooks.
> 
> If your function doesn't call any Hooks, avoid the `use` prefix. Instead, write it as a regular function *without* the `use` prefix. For example, `useSorted` below doesn't call Hooks, so call it `getSorted` instead:
> 
> ```js
> // 🔴 Avoid: A Hook that doesn't use Hooks
> function useSorted(items) {
>   return items.slice().sort();
> }
> 
> // ✅ Good: A regular function that doesn't use Hooks
> function getSorted(items) {
>   return items.slice().sort();
> }
> ```
> 
> This ensures that your code can call this regular function anywhere, including conditions:
> 
> ```js
> function List({ items, shouldSort }) {
>   let displayedItems = items;
>   if (shouldSort) {
>     // ✅ It's ok to call getSorted() conditionally because it's not a Hook
>     displayedItems = getSorted(items);
>   }
>   // ...
> }
> ```
> 
> You should give `use` prefix to a function (and thus make it a Hook) if it uses at least one Hook inside of it:
> 
> ```js
> // ✅ Good: A Hook that uses other Hooks
> function useAuth() {
>   return useContext(Auth);
> }
> ```
> 
> Technically, this isn't enforced by React. In principle, you could make a Hook that doesn't call other Hooks. This is often confusing and limiting so it's best to avoid that pattern. However, there may be rare cases where it is helpful. For example, maybe your function doesn't use any Hooks right now, but you plan to add some Hook calls to it in the future. Then it makes sense to name it with the `use` prefix:
> 
> ```js {3-4}
> // ✅ Good: A Hook that will likely use some other Hooks later
> function useAuth() {
>   // TODO: Replace with this line when authentication is implemented:
>   // return useContext(Auth);
>   return TEST_USER;
> }
> ```
> 
> Then components won't be able to call it conditionally. This will become important when you actually add Hook calls inside. If you don't plan to use Hooks inside it (now or later), don't make it a Hook.


### Custom Hooks let you share stateful logic, not state itself {/*custom-hooks-let-you-share-stateful-logic-not-state-itself*/}

In the earlier example, when you turned the network on and off, both components updated together. However, it's wrong to think that a single `isOnline` state variable is shared between them. Look at this code:

```js {2,7}
function StatusBar() {
  const isOnline = useOnlineStatus();
  // ...
}

function SaveButton() {
  const isOnline = useOnlineStatus();
  // ...
}
```

It works the same way as before you extracted the duplication:

```js {2-5,10-13}
function StatusBar() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    // ...
  }, []);
  // ...
}

function SaveButton() {
  const [isOnline, setIsOnline] = useState(true);
  useEffect(() => {
    // ...
  }, []);
  // ...
}
```

These are two completely independent state variables and Effects! They happened to have the same value at the same time because you synchronized them with the same external value (whether the network is on).

To better illustrate this, we'll need a different example. Consider this `Form` component:

[Interactive example removed — see react.dev for live demo]


There's some repetitive logic for each form field:

1. There's a piece of state (`firstName` and `lastName`).
1. There's a change handler (`handleFirstNameChange` and `handleLastNameChange`).
1. There's a piece of JSX that specifies the `value` and `onChange` attributes for that input.

You can extract the repetitive logic into this `useFormInput` custom Hook:

[Interactive example removed — see react.dev for live demo]


Notice that it only declares *one* state variable called `value`.

However, the `Form` component calls `useFormInput` *two times:*

```js
function Form() {
  const firstNameProps = useFormInput('Mary');
  const lastNameProps = useFormInput('Poppins');
  // ...
```

This is why it works like declaring two separate state variables!

**Custom Hooks let you share *stateful logic* but not *state itself.* Each call to a Hook is completely independent from every other call to the same Hook.** This is why the two sandboxes above are completely equivalent. If you'd like, scroll back up and compare them. The behavior before and after extracting a custom Hook is identical.

When you need to share the state itself between multiple components, [lift it up and pass it down](/learn/sharing-state-between-components) instead.

## Passing reactive values between Hooks {/*passing-reactive-values-between-hooks*/}

The code inside your custom Hooks will re-run during every re-render of your component. This is why, like components, custom Hooks [need to be pure.](/learn/keeping-components-pure) Think of custom Hooks' code as part of your component's body!

Because custom Hooks re-render together with your component, they always receive the latest props and state. To see what this means, consider this chat room example. Change the server URL or the chat room:

[Interactive example removed — see react.dev for live demo]


When you change `serverUrl` or `roomId`, the Effect ["reacts" to your changes](/learn/lifecycle-of-reactive-effects#effects-react-to-reactive-values) and re-synchronizes. You can tell by the console messages that the chat re-connects every time that you change your Effect's dependencies.

Now move the Effect's code into a custom Hook:

```js {2-13}
export function useChatRoom({ serverUrl, roomId }) {
  useEffect(() => {
    const options = {
      serverUrl: serverUrl,
      roomId: roomId
    };
    const connection = createConnection(options);
    connection.connect();
    connection.on('message', (msg) => {
      showNotification('New message: ' + msg);
    });
    return () => connection.disconnect();
  }, [roomId, serverUrl]);
}
```

This lets your `ChatRoom` component call your custom Hook without worrying about how it works inside:

```js {4-7}
export default function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useChatRoom({
    roomId: roomId,
    serverUrl: serverUrl
  });

  return (
    <>
      <label>
        Server URL:
        <input value={serverUrl} onChange={e => setServerUrl(e.target.value)} />
      </label>
      <h1>Welcome to the {roomId} room!</h1>
    </>
  );
}
```

This looks much simpler! (But it does the same thing.)

Notice that the logic *still responds* to prop and state changes. Try editing the server URL or the selected room:

[Interactive example removed — see react.dev for live demo]


Notice how you're taking the return value of one Hook:

```js {2}
export default function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useChatRoom({
    roomId: roomId,
    serverUrl: serverUrl
  });
  // ...
```

and passing it as an input to another Hook:

```js {6}
export default function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useChatRoom({
    roomId: roomId,
    serverUrl: serverUrl
  });
  // ...
```

Every time your `ChatRoom` component re-renders, it passes the latest `roomId` and `serverUrl` to your Hook. This is why your Effect re-connects to the chat whenever their values are different after a re-render. (If you ever worked with audio or video processing software, chaining Hooks like this might remind you of chaining visual or audio effects. It's as if the output of `useState` "feeds into" the input of the `useChatRoom`.)

### Passing event handlers to custom Hooks {/*passing-event-handlers-to-custom-hooks*/}

As you start using `useChatRoom` in more components, you might want to let components customize its behavior. For example, currently, the logic for what to do when a message arrives is hardcoded inside the Hook:

```js {9-11}
export function useChatRoom({ serverUrl, roomId }) {
  useEffect(() => {
    const options = {
      serverUrl: serverUrl,
      roomId: roomId
    };
    const connection = createConnection(options);
    connection.connect();
    connection.on('message', (msg) => {
      showNotification('New message: ' + msg);
    });
    return () => connection.disconnect();
  }, [roomId, serverUrl]);
}
```

Let's say you want to move this logic back to your component:

```js {7-9}
export default function ChatRoom({ roomId }) {
  const [serverUrl, setServerUrl] = useState('https://localhost:1234');

  useChatRoom({
    roomId: roomId,
    serverUrl: serverUrl,
    onReceiveMessage(msg) {
      showNotification('New message: ' + msg);
    }
  });
  // ...
```

To make this work, change your custom Hook to take `onReceiveMessage` as one of its named options:

```js {1,10,13}
export function useChatRoom({ serverUrl, roomId, onReceiveMessage }) {
  useEffect(() => {
    const options = {
      serverUrl: serverUrl,
      roomId: roomId
    };
    const connection = createConnection(options);
    connection.connect();
    connection.on('message', (msg) => {
      onReceiveMessage(msg);
    });
    return () => connection.disconnect();
  }, [roomId, serverUrl, onReceiveMessage]); // ✅ All dependencies declared
}
```

This will work, but there's one more improvement you can do when your custom Hook accepts event handlers.

Adding a dependency on `onReceiveMessage` is not ideal because it will cause the chat to re-connect every time the component re-renders. [Wrap this event handler into an Effect Event to remove it from the dependencies:](/learn/removing-effect-dependencies#wrapping-an-event-handler-from-the-props)

```js {1,4,5,15,18}
import { useEffect, useEffectEvent } from 'react';
// ...

export function useChatRoom({ serverUrl, roomId, onReceiveMessage }) {
  const onMessage = useEffectEvent(onReceiveMessage);

  useEffect(() => {
    const options = {
      serverUrl: serverUrl,
      roomId: roomId
    };
    const connection = createConnection(options);
    connection.connect();
    connection.on('message', (msg) => {
      onMessage(msg);
    });
    return () => connection.disconnect();
  }, [roomId, serverUrl]); // ✅ All dependencies declared
}
```

Now the chat won't re-connect every time that the `ChatRoom` component re-renders. Here is a fully working demo of passing an event handler to a custom Hook that you can play with:

[Interactive example removed — see react.dev for live demo]


Notice how you no longer need to know *how* `useChatRoom` works in order to use it. You could add it to any other component, pass any other options, and it would work the same way. That's the power of custom Hooks.

## When to use custom Hooks {/*when-to-use-custom-hooks*/}

You don't need to extract a custom Hook for every little duplicated bit of code. Some duplication is fine. For example, extracting a `useFormInput` Hook to wrap a single `useState` call like earlier is probably unnecessary.

However, whenever you write an Effect, consider whether it would be clearer to also wrap it in a custom Hook. [You shouldn't need Effects very often,](/learn/you-might-not-need-an-effect) so if you're writing one, it means that you need to "step outside React" to synchronize with some external system or to do something that React doesn't have a built-in API for. Wrapping it into a custom Hook lets you precisely communicate your intent and how the data flows through it.

For example, consider a `ShippingForm` component that displays two dropdowns: one shows the list of cities, and another shows the list of areas in the selected city. You might start with some code that looks like this:

```js {3-16,20-35}
function ShippingForm({ country }) {
  const [cities, setCities] = useState(null);
  // This Effect fetches cities for a country
  useEffect(() => {
    let ignore = false;
    fetch(`/api/cities?country=${country}`)
      .then(response => response.json())
      .then(json => {
        if (!ignore) {
          setCities(json);
        }
      });
    return () => {
      ignore = true;
    };
  }, [country]);

  const [city, setCity] = useState(null);
  const [areas, setAreas] = useState(null);
  // This Effect fetches areas for the selected city
  useEffect(() => {
    if (city) {
      let ignore = false;
      fetch(`/api/areas?city=${city}`)
        .then(response => response.json())
        .then(json => {
          if (!ignore) {
            setAreas(json);
          }
        });
      return () => {
        ignore = true;
      };
    }
  }, [city]);

  // ...
```

Although this code is quite repetitive, [it's correct to keep these Effects separate from each other.](/learn/removing-effect-dependencies#is-your-effect-doing-several-unrelated-things) They synchronize two different things, so you shouldn't merge them into one Effect. Instead, you can simplify the `ShippingForm` component above by extracting the common logic between them into your own `useData` Hook:

```js {2-18}
function useData(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    if (url) {
      let ignore = false;
      fetch(url)
        .then(response => response.json())
        .then(json => {
          if (!ignore) {
            setData(json);
          }
        });
      return () => {
        ignore = true;
      };
    }
  }, [url]);
  return data;
}
```

Now you can replace both Effects in the `ShippingForm` components with calls to `useData`:

```js {2,4}
function ShippingForm({ country }) {
  const cities = useData(`/api/cities?country=${country}`);
  const [city, setCity] = useState(null);
  const areas = useData(city ? `/api/areas?city=${city}` : null);
  // ...
```

Extracting a custom Hook makes the data flow explicit. You feed the `url` in and you get the `data` out. By "hiding" your Effect inside `useData`, you also prevent someone working on the `ShippingForm` component from adding [unnecessary dependencies](/learn/removing-effect-dependencies) to it. With time, most of your app's Effects will be in custom Hooks.

> **Deep Dive: Keep your custom Hooks focused on concrete high-level use cases {/*keep-your-custom-hooks-focused-on-concrete-high-level-use-cases*/}**
>
> Start by choosing your custom Hook's name. If you struggle to pick a clear name, it might mean that your Effect is too coupled to the rest of your component's logic, and is not yet ready to be extracted.
> 
> Ideally, your custom Hook's name should be clear enough that even a person who doesn't write code often could have a good guess about what your custom Hook does, what it takes, and what it returns:
> 
> * ✅ `useData(url)`
> * ✅ `useImpressionLog(eventName, extraData)`
> * ✅ `useChatRoom(options)`
> 
> When you synchronize with an external system, your custom Hook name may be more technical and use jargon specific to that system. It's good as long as it would be clear to a person familiar with that system:
> 
> * ✅ `useMediaQuery(query)`
> * ✅ `useSocket(url)`
> * ✅ `useIntersectionObserver(ref, options)`
> 
> **Keep custom Hooks focused on concrete high-level use cases.** Avoid creating and using custom "lifecycle" Hooks that act as alternatives and convenience wrappers for the `useEffect` API itself:
> 
> * 🔴 `useMount(fn)`
> * 🔴 `useEffectOnce(fn)`
> * 🔴 `useUpdateEffect(fn)`
> 
> For example, this `useMount` Hook tries to ensure some code only runs "on mount":
> 
> ```js {4-5,14-15}
> function ChatRoom({ roomId }) {
>   const [serverUrl, setServerUrl] = useState('https://localhost:1234');
> 
>   // 🔴 Avoid: using custom "lifecycle" Hooks
>   useMount(() => {
>     const connection = createConnection({ roomId, serverUrl });
>     connection.connect();
> 
>     post('/analytics/event', { eventName: 'visit_chat' });
>   });
>   // ...
> }
> 
> // 🔴 Avoid: creating custom "lifecycle" Hooks
> function useMount(fn) {
>   useEffect(() => {
>     fn();
>   }, []); // 🔴 React Hook useEffect has a missing dependency: 'fn'
> }
> ```
> 
> **Custom "lifecycle" Hooks like `useMount` don't fit well into the React paradigm.** For example, this code example has a mistake (it doesn't "react" to `roomId` or `serverUrl` changes), but the linter won't warn you about it because the linter only checks direct `useEffect` calls. It won't know about your Hook.
> 
> If you're writing an Effect, start by using the React API directly:
> 
> ```js
> function ChatRoom({ roomId }) {
>   const [serverUrl, setServerUrl] = useState('https://localhost:1234');
> 
>   // ✅ Good: two raw Effects separated by purpose
> 
>   useEffect(() => {
>     const connection = createConnection({ serverUrl, roomId });
>     connection.connect();
>     return () => connection.disconnect();
>   }, [serverUrl, roomId]);
> 
>   useEffect(() => {
>     post('/analytics/event', { eventName: 'visit_chat', roomId });
>   }, [roomId]);
> 
>   // ...
> }
> ```
> 
> Then, you can (but don't have to) extract custom Hooks for different high-level use cases:
> 
> ```js
> function ChatRoom({ roomId }) {
>   const [serverUrl, setServerUrl] = useState('https://localhost:1234');
> 
>   // ✅ Great: custom Hooks named after their purpose
>   useChatRoom({ serverUrl, roomId });
>   useImpressionLog('visit_chat', { roomId });
>   // ...
> }
> ```
> 
> **A good custom Hook makes the calling code more declarative by constraining what it does.** For example, `useChatRoom(options)` can only connect to the chat room, while `useImpressionLog(eventName, extraData)` can only send an impression log to the analytics. If your custom Hook API doesn't constrain the use cases and is very abstract, in the long run it's likely to introduce more problems than it solves.


### Custom Hooks help you migrate to better patterns {/*custom-hooks-help-you-migrate-to-better-patterns*/}

Effects are an ["escape hatch"](/learn/escape-hatches): you use them when you need to "step outside React" and when there is no better built-in solution for your use case. With time, the React team's goal is to reduce the number of the Effects in your app to the minimum by providing more specific solutions to more specific problems. Wrapping your Effects in custom Hooks makes it easier to upgrade your code when these solutions become available.

Let's return to this example:

[Interactive example removed — see react.dev for live demo]


In the above example, `useOnlineStatus` is implemented with a pair of [`useState`](/reference/react/useState) and [`useEffect`.](/reference/react/useEffect) However, this isn't the best possible solution. There is a number of edge cases it doesn't consider. For example, it assumes that when the component mounts, `isOnline` is already `true`, but this may be wrong if the network already went offline. You can use the browser [`navigator.onLine`](https://developer.mozilla.org/en-US/docs/Web/API/Navigator/onLine) API to check for that, but using it directly would not work on the server for generating the initial HTML. In short, this code could be improved.

React includes a dedicated API called [`useSyncExternalStore`](/reference/react/useSyncExternalStore) which takes care of all of these problems for you. Here is your `useOnlineStatus` Hook, rewritten to take advantage of this new API:

[Interactive example removed — see react.dev for live demo]


Notice how **you didn't need to change any of the components** to make this migration:

```js {2,7}
function StatusBar() {
  const isOnline = useOnlineStatus();
  // ...
}

function SaveButton() {
  const isOnline = useOnlineStatus();
  // ...
}
```

This is another reason for why wrapping Effects in custom Hooks is often beneficial:

1. You make the data flow to and from your Effects very explicit.
2. You let your components focus on the intent rather than on the exact implementation of your Effects.
3. When React adds new features, you can remove those Effects without changing any of your components.

Similar to a [design system,](https://uxdesign.cc/everything-you-need-to-know-about-design-systems-54b109851969) you might find it helpful to start extracting common idioms from your app's components into custom Hooks. This will keep your components' code focused on the intent, and let you avoid writing raw Effects very often. Many excellent custom Hooks are maintained by the React community.

> **Deep Dive: Will React provide any built-in solution for data fetching? {/*will-react-provide-any-built-in-solution-for-data-fetching*/}**
>
> Today, with the [`use`](/reference/react/use#streaming-data-from-server-to-client) API, data can be read in render by passing a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) to `use`:
> 
> ```js {1,4,11}
> import { use, Suspense } from "react";
> 
> function Message({ messagePromise }) {
>   const messageContent = use(messagePromise);
>   return <p>Here is the message: {messageContent}</p>;
> }
> 
> export function MessageContainer({ messagePromise }) {
>   return (
>     <Suspense fallback={<p>⌛Downloading message...</p>}>
>       <Message messagePromise={messagePromise} />
>     </Suspense>
>   );
> }
> ```
> 
> We're still working out the details, but we expect that in the future, you'll write data fetching like this:
> 
> ```js {1,4,6}
> import { use } from 'react';
> 
> function ShippingForm({ country }) {
>   const cities = use(fetch(`/api/cities?country=${country}`));
>   const [city, setCity] = useState(null);
>   const areas = city ? use(fetch(`/api/areas?city=${city}`)) : null;
>   // ...
> ```
> 
> If you use custom Hooks like `useData` above in your app, it will require fewer changes to migrate to the eventually recommended approach than if you write raw Effects in every component manually. However, the old approach will still work fine, so if you feel happy writing raw Effects, you can continue to do that.


### There is more than one way to do it {/*there-is-more-than-one-way-to-do-it*/}

Let's say you want to implement a fade-in animation *from scratch* using the browser [`requestAnimationFrame`](https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame) API. You might start with an Effect that sets up an animation loop. During each frame of the animation, you could change the opacity of the DOM node you [hold in a ref](/learn/manipulating-the-dom-with-refs) until it reaches `1`. Your code might start like this:

[Interactive example removed — see react.dev for live demo]


To make the component more readable, you might extract the logic into a `useFadeIn` custom Hook:

[Interactive example removed — see react.dev for live demo]


You could keep the `useFadeIn` code as is, but you could also refactor it more. For example, you could extract the logic for setting up the animation loop out of `useFadeIn` into a custom `useAnimationLoop` Hook:

[Interactive example removed — see react.dev for live demo]


However, you didn't *have to* do that. As with regular functions, ultimately you decide where to draw the boundaries between different parts of your code. You could also take a very different approach. Instead of keeping the logic in the Effect, you could move most of the imperative logic inside a JavaScript [class:](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes)

[Interactive example removed — see react.dev for live demo]


Effects let you connect React to external systems. The more coordination between Effects is needed (for example, to chain multiple animations), the more it makes sense to extract that logic out of Effects and Hooks *completely* like in the sandbox above. Then, the code you extracted *becomes* the "external system". This lets your Effects stay simple because they only need to send messages to the system you've moved outside React.

The examples above assume that the fade-in logic needs to be written in JavaScript. However, this particular fade-in animation is both simpler and much more efficient to implement with a plain [CSS Animation:](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations/Using_CSS_animations)

[Interactive example removed — see react.dev for live demo]


Sometimes, you don't even need a Hook!

- Custom Hooks let you share logic between components.
- Custom Hooks must be named starting with `use` followed by a capital letter.
- Custom Hooks only share stateful logic, not state itself.
- You can pass reactive values from one Hook to another, and they stay up-to-date.
- All Hooks re-run every time your component re-renders.
- The code of your custom Hooks should be pure, like your component's code.
- Wrap event handlers received by custom Hooks into Effect Events.
- Don't create custom Hooks like `useMount`. Keep their purpose specific.
- It's up to you how and where to choose the boundaries of your code.




# Usedebugvalue

`useDebugValue` is a React Hook that lets you add a label to a custom Hook in [React DevTools.](/learn/react-developer-tools)

```js
useDebugValue(value, format?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useDebugValue(value, format?)` {/*usedebugvalue*/}

Call `useDebugValue` at the top level of your [custom Hook](/learn/reusing-logic-with-custom-hooks) to display a readable debug value:

```js
import { useDebugValue } from 'react';

function useOnlineStatus() {
  // ...
  useDebugValue(isOnline ? 'Online' : 'Offline');
  // ...
}
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `value`: The value you want to display in React DevTools. It can have any type.
* **optional** `format`: A formatting function. When the component is inspected, React DevTools will call the formatting function with the `value` as the argument, and then display the returned formatted value (which may have any type). If you don't specify the formatting function, the original `value` itself will be displayed.

#### Returns {/*returns*/}

`useDebugValue` does not return anything.

## Usage {/*usage*/}

### Adding a label to a custom Hook {/*adding-a-label-to-a-custom-hook*/}

Call `useDebugValue` at the top level of your [custom Hook](/learn/reusing-logic-with-custom-hooks) to display a readable debug value for [React DevTools.](/learn/react-developer-tools)

```js [[1, 5, "isOnline ? 'Online' : 'Offline'"]]
import { useDebugValue } from 'react';

function useOnlineStatus() {
  // ...
  useDebugValue(isOnline ? 'Online' : 'Offline');
  // ...
}
```

This gives components calling `useOnlineStatus` a label like `OnlineStatus: "Online"` when you inspect them:

![A screenshot of React DevTools showing the debug value](/images/docs/react-devtools-usedebugvalue.png)

Without the `useDebugValue` call, only the underlying data (in this example, `true`) would be displayed.

[Interactive example removed — see react.dev for live demo]


> **Note:**
>
> 
> 
> Don't add debug values to every custom Hook. It's most valuable for custom Hooks that are part of shared libraries and that have a complex internal data structure that's difficult to inspect.
> 
> 


---

### Deferring formatting of a debug value {/*deferring-formatting-of-a-debug-value*/}

You can also pass a formatting function as the second argument to `useDebugValue`:

```js [[1, 1, "date", 18], [2, 1, "date.toDateString()"]]
useDebugValue(date, date => date.toDateString());
```

Your formatting function will receive the debug value as a parameter and should return a formatted display value. When your component is inspected, React DevTools will call this function and display its result.

This lets you avoid running potentially expensive formatting logic unless the component is actually inspected. For example, if `date` is a Date value, this avoids calling `toDateString()` on it for every render.
