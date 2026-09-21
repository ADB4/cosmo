---
title: React Refs And Dom
source: react.dev
syllabus_weeks: [7]
topics: [useRef, ref, DOM manipulation, useImperativeHandle, forwardRef, createPortal, flushSync]
---



# Referencing Values With Refs

When you want a component to "remember" some information, but you don't want that information to [trigger new renders](/learn/render-and-commit), you can use a *ref*.

- How to add a ref to your component
- How to update a ref's value
- How refs are different from state
- How to use refs safely

## Adding a ref to your component {/*adding-a-ref-to-your-component*/}

You can add a ref to your component by importing the `useRef` Hook from React:

```js
import { useRef } from 'react';
```

Inside your component, call the `useRef` Hook and pass the initial value that you want to reference as the only argument. For example, here is a ref to the value `0`:

```js
const ref = useRef(0);
```

`useRef` returns an object like this:

```js
{ 
  current: 0 // The value you passed to useRef
}
```

<Illustration src="/images/docs/illustrations/i_ref.png" alt="An arrow with 'current' written on it stuffed into a pocket with 'ref' written on it." />

You can access the current value of that ref through the `ref.current` property. This value is intentionally mutable, meaning you can both read and write to it. It's like a secret pocket of your component that React doesn't track. (This is what makes it an "escape hatch" from React's one-way data flow--more on that below!)

Here, a button will increment `ref.current` on every click:

[Interactive example removed — see react.dev for live demo]


The ref points to a number, but, like [state](/learn/state-a-components-memory), you could point to anything: a string, an object, or even a function. Unlike state, ref is a plain JavaScript object with the `current` property that you can read and modify.

Note that **the component doesn't re-render with every increment.** Like state, refs are retained by React between re-renders. However, setting state re-renders a component. Changing a ref does not!

## Example: building a stopwatch {/*example-building-a-stopwatch*/}

You can combine refs and state in a single component. For example, let's make a stopwatch that the user can start or stop by pressing a button. In order to display how much time has passed since the user pressed "Start", you will need to keep track of when the Start button was pressed and what the current time is. **This information is used for rendering, so you'll keep it in state:**

```js
const [startTime, setStartTime] = useState(null);
const [now, setNow] = useState(null);
```

When the user presses "Start", you'll use [`setInterval`](https://developer.mozilla.org/docs/Web/API/setInterval) in order to update the time every 10 milliseconds:

[Interactive example removed — see react.dev for live demo]


When the "Stop" button is pressed, you need to cancel the existing interval so that it stops updating the `now` state variable. You can do this by calling [`clearInterval`](https://developer.mozilla.org/en-US/docs/Web/API/clearInterval), but you need to give it the interval ID that was previously returned by the `setInterval` call when the user pressed Start. You need to keep the interval ID somewhere. **Since the interval ID is not used for rendering, you can keep it in a ref:**

[Interactive example removed — see react.dev for live demo]


When a piece of information is used for rendering, keep it in state. When a piece of information is only needed by event handlers and changing it doesn't require a re-render, using a ref may be more efficient.

## Differences between refs and state {/*differences-between-refs-and-state*/}

Perhaps you're thinking refs seem less "strict" than state—you can mutate them instead of always having to use a state setting function, for instance. But in most cases, you'll want to use state. Refs are an "escape hatch" you won't need often. Here's how state and refs compare:

| refs                                                                                  | state                                                                                                                     |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `useRef(initialValue)` returns `{ current: initialValue }`                            | `useState(initialValue)` returns the current value of a state variable and a state setter function ( `[value, setValue]`) |
| Doesn't trigger re-render when you change it.                                         | Triggers re-render when you change it.                                                                                    |
| Mutable—you can modify and update `current`'s value outside of the rendering process. | "Immutable"—you must use the state setting function to modify state variables to queue a re-render.                       |
| You shouldn't read (or write) the `current` value during rendering. | You can read state at any time. However, each render has its own [snapshot](/learn/state-as-a-snapshot) of state which does not change.

Here is a counter button that's implemented with state:

[Interactive example removed — see react.dev for live demo]


Because the `count` value is displayed, it makes sense to use a state value for it. When the counter's value is set with `setCount()`, React re-renders the component and the screen updates to reflect the new count.

If you tried to implement this with a ref, React would never re-render the component, so you'd never see the count change! See how clicking this button **does not update its text**:

[Interactive example removed — see react.dev for live demo]


This is why reading `ref.current` during render leads to unreliable code. If you need that, use state instead.

> **Deep Dive: How does useRef work inside? {/*how-does-use-ref-work-inside*/}**
>
> Although both `useState` and `useRef` are provided by React, in principle `useRef` could be implemented _on top of_ `useState`. You can imagine that inside of React, `useRef` is implemented like this:
> 
> ```js
> // Inside of React
> function useRef(initialValue) {
>   const [ref, unused] = useState({ current: initialValue });
>   return ref;
> }
> ```
> 
> During the first render, `useRef` returns `{ current: initialValue }`. This object is stored by React, so during the next render the same object will be returned. Note how the state setter is unused in this example. It is unnecessary because `useRef` always needs to return the same object!
> 
> React provides a built-in version of `useRef` because it is common enough in practice. But you can think of it as a regular state variable without a setter. If you're familiar with object-oriented programming, refs might remind you of instance fields--but instead of `this.something` you write `somethingRef.current`.


## When to use refs {/*when-to-use-refs*/}

Typically, you will use a ref when your component needs to "step outside" React and communicate with external APIs—often a browser API that won't impact the appearance of the component. Here are a few of these rare situations:

- Storing [timeout IDs](https://developer.mozilla.org/docs/Web/API/setTimeout)
- Storing and manipulating [DOM elements](https://developer.mozilla.org/docs/Web/API/Element), which we cover on [the next page](/learn/manipulating-the-dom-with-refs)
- Storing other objects that aren't necessary to calculate the JSX.

If your component needs to store some value, but it doesn't impact the rendering logic, choose refs.

## Best practices for refs {/*best-practices-for-refs*/}

Following these principles will make your components more predictable:

- **Treat refs as an escape hatch.** Refs are useful when you work with external systems or browser APIs. If much of your application logic and data flow relies on refs, you might want to rethink your approach.
- **Don't read or write `ref.current` during rendering.** If some information is needed during rendering, use [state](/learn/state-a-components-memory) instead. Since React doesn't know when `ref.current` changes, even reading it while rendering makes your component's behavior difficult to predict. (The only exception to this is code like `if (!ref.current) ref.current = new Thing()` which only sets the ref once during the first render.)

Limitations of React state don't apply to refs. For example, state acts like a [snapshot for every render](/learn/state-as-a-snapshot) and [doesn't update synchronously.](/learn/queueing-a-series-of-state-updates) But when you mutate the current value of a ref, it changes immediately:

```js
ref.current = 5;
console.log(ref.current); // 5
```

This is because **the ref itself is a regular JavaScript object,** and so it behaves like one.

You also don't need to worry about [avoiding mutation](/learn/updating-objects-in-state) when you work with a ref. As long as the object you're mutating isn't used for rendering, React doesn't care what you do with the ref or its contents.

## Refs and the DOM {/*refs-and-the-dom*/}

You can point a ref to any value. However, the most common use case for a ref is to access a DOM element. For example, this is handy if you want to focus an input programmatically. When you pass a ref to a `ref` attribute in JSX, like `<div ref={myRef}>`, React will put the corresponding DOM element into `myRef.current`. Once the element is removed from the DOM, React will update `myRef.current` to be `null`. You can read more about this in [Manipulating the DOM with Refs.](/learn/manipulating-the-dom-with-refs)

- Refs are an escape hatch to hold onto values that aren't used for rendering. You won't need them often.
- A ref is a plain JavaScript object with a single property called `current`, which you can read or set.
- You can ask React to give you a ref by calling the `useRef` Hook.
- Like state, refs let you retain information between re-renders of a component.
- Unlike state, setting the ref's `current` value does not trigger a re-render.
- Don't read or write `ref.current` during rendering. This makes your component hard to predict.






# Manipulating The Dom With Refs

React automatically updates the [DOM](https://developer.mozilla.org/docs/Web/API/Document_Object_Model/Introduction) to match your render output, so your components won't often need to manipulate it. However, sometimes you might need access to the DOM elements managed by React--for example, to focus a node, scroll to it, or measure its size and position. There is no built-in way to do those things in React, so you will need a *ref* to the DOM node.

- How to access a DOM node managed by React with the `ref` attribute
- How the `ref` JSX attribute relates to the `useRef` Hook
- How to access another component's DOM node
- In which cases it's safe to modify the DOM managed by React

## Getting a ref to the node {/*getting-a-ref-to-the-node*/}

To access a DOM node managed by React, first, import the `useRef` Hook:

```js
import { useRef } from 'react';
```

Then, use it to declare a ref inside your component:

```js
const myRef = useRef(null);
```

Finally, pass your ref as the `ref` attribute to the JSX tag for which you want to get the DOM node:

```js
<div ref={myRef}>
```

The `useRef` Hook returns an object with a single property called `current`. Initially, `myRef.current` will be `null`. When React creates a DOM node for this `<div>`, React will put a reference to this node into `myRef.current`. You can then access this DOM node from your [event handlers](/learn/responding-to-events) and use the built-in [browser APIs](https://developer.mozilla.org/docs/Web/API/Element) defined on it.

```js
// You can use any browser APIs, for example:
myRef.current.scrollIntoView();
```

### Example: Focusing a text input {/*example-focusing-a-text-input*/}

In this example, clicking the button will focus the input:

[Interactive example removed — see react.dev for live demo]


To implement this:

1. Declare `inputRef` with the `useRef` Hook.
2. Pass it as `<input ref={inputRef}>`. This tells React to **put this `<input>`'s DOM node into `inputRef.current`.**
3. In the `handleClick` function, read the input DOM node from `inputRef.current` and call [`focus()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) on it with `inputRef.current.focus()`.
4. Pass the `handleClick` event handler to `<button>` with `onClick`.

While DOM manipulation is the most common use case for refs, the `useRef` Hook can be used for storing other things outside React, like timer IDs. Similarly to state, refs remain between renders. Refs are like state variables that don't trigger re-renders when you set them. Read about refs in [Referencing Values with Refs.](/learn/referencing-values-with-refs)

### Example: Scrolling to an element {/*example-scrolling-to-an-element*/}

You can have more than a single ref in a component. In this example, there is a carousel of three images. Each button centers an image by calling the browser [`scrollIntoView()`](https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView) method on the corresponding DOM node:

[Interactive example removed — see react.dev for live demo]


> **Deep Dive: How to manage a list of refs using a ref callback {/*how-to-manage-a-list-of-refs-using-a-ref-callback*/}**
>
> In the above examples, there is a predefined number of refs. However, sometimes you might need a ref to each item in the list, and you don't know how many you will have. Something like this **wouldn't work**:
> 
> ```js
> <ul>
>   {items.map((item) => {
>     // Doesn't work!
>     const ref = useRef(null);
>     return <li ref={ref} />;
>   })}
> </ul>
> ```
> 
> This is because **Hooks must only be called at the top-level of your component.** You can't call `useRef` in a loop, in a condition, or inside a `map()` call.
> 
> One possible way around this is to get a single ref to their parent element, and then use DOM manipulation methods like [`querySelectorAll`](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelectorAll) to "find" the individual child nodes from it. However, this is brittle and can break if your DOM structure changes.
> 
> Another solution is to **pass a function to the `ref` attribute.** This is called a [`ref` callback.](/reference/react-dom/components/common#ref-callback) React will call your ref callback with the DOM node when it's time to set the ref, and call the cleanup function returned from the callback when it's time to clear it. This lets you maintain your own array or a [Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map), and access any ref by its index or some kind of ID.
> 
> This example shows how you can use this approach to scroll to an arbitrary node in a long list:
> 
> [Interactive example removed — see react.dev for live demo]
> 
> 
> In this example, `itemsRef` doesn't hold a single DOM node. Instead, it holds a [Map](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/Map) from item ID to a DOM node. ([Refs can hold any values!](/learn/referencing-values-with-refs)) The [`ref` callback](/reference/react-dom/components/common#ref-callback) on every list item takes care to update the Map:
> 
> ```js
> <li
>   key={cat.id}
>   ref={node => {
>     const map = getMap();
>     // Add to the Map
>     map.set(cat, node);
> 
>     return () => {
>       // Remove from the Map
>       map.delete(cat);
>     };
>   }}
> >
> ```
> 
> This lets you read individual DOM nodes from the Map later.
> 
> <Note>
> 
> When Strict Mode is enabled, ref callbacks will run twice in development.
> 
> Read more about [how this helps find bugs](/reference/react/StrictMode#fixing-bugs-found-by-re-running-ref-callbacks-in-development) in callback refs.
> 
> </Note>


## Accessing another component's DOM nodes {/*accessing-another-components-dom-nodes*/}

> **Pitfall:**
>
> 
> Refs are an escape hatch. Manually manipulating _another_ component's DOM nodes can make your code fragile.
> 


You can pass refs from parent component to child components [just like any other prop](/learn/passing-props-to-a-component).

```js {3-4,9}
import { useRef } from 'react';

function MyInput({ ref }) {
  return <input ref={ref} />;
}

function MyForm() {
  const inputRef = useRef(null);
  return <MyInput ref={inputRef} />
}
```

In the above example, a ref is created in the parent component, `MyForm`, and is passed to the child component, `MyInput`. `MyInput` then passes the ref to `<input>`. Because `<input>` is a [built-in component](/reference/react-dom/components/common) React sets the `.current` property of the ref to the `<input>` DOM element.

The `inputRef` created in `MyForm` now points to the `<input>` DOM element returned by `MyInput`. A click handler created in `MyForm` can access `inputRef` and call `focus()` to set the focus on `<input>`.

[Interactive example removed — see react.dev for live demo]


> **Deep Dive: Exposing a subset of the API with an imperative handle {/*exposing-a-subset-of-the-api-with-an-imperative-handle*/}**
>
> In the above example, the ref passed to `MyInput` is passed on to the original DOM input element. This lets the parent component call `focus()` on it. However, this also lets the parent component do something else--for example, change its CSS styles. In uncommon cases, you may want to restrict the exposed functionality. You can do that with [`useImperativeHandle`](/reference/react/useImperativeHandle):
> 
> [Interactive example removed — see react.dev for live demo]
> 
> 
> Here, `realInputRef` inside `MyInput` holds the actual input DOM node. However, [`useImperativeHandle`](/reference/react/useImperativeHandle) instructs React to provide your own special object as the value of a ref to the parent component. So `inputRef.current` inside the `Form` component will only have the `focus` method. In this case, the ref "handle" is not the DOM node, but the custom object you create inside [`useImperativeHandle`](/reference/react/useImperativeHandle) call.


## When React attaches the refs {/*when-react-attaches-the-refs*/}

In React, every update is split in [two phases](/learn/render-and-commit#step-3-react-commits-changes-to-the-dom):

* During **render,** React calls your components to figure out what should be on the screen.
* During **commit,** React applies changes to the DOM.

In general, you [don't want](/learn/referencing-values-with-refs#best-practices-for-refs) to access refs during rendering. That goes for refs holding DOM nodes as well. During the first render, the DOM nodes have not yet been created, so `ref.current` will be `null`. And during the rendering of updates, the DOM nodes haven't been updated yet. So it's too early to read them.

React sets `ref.current` during the commit. Before updating the DOM, React sets the affected `ref.current` values to `null`. After updating the DOM, React immediately sets them to the corresponding DOM nodes.

**Usually, you will access refs from event handlers.** If you want to do something with a ref, but there is no particular event to do it in, you might need an Effect. We will discuss Effects on the next pages.

> **Deep Dive: Flushing state updates synchronously with flushSync {/*flushing-state-updates-synchronously-with-flush-sync*/}**
>
> Consider code like this, which adds a new todo and scrolls the screen down to the last child of the list. Notice how, for some reason, it always scrolls to the todo that was *just before* the last added one:
> 
> [Interactive example removed — see react.dev for live demo]
> 
> 
> The issue is with these two lines:
> 
> ```js
> setTodos([ ...todos, newTodo]);
> listRef.current.lastChild.scrollIntoView();
> ```
> 
> In React, [state updates are queued.](/learn/queueing-a-series-of-state-updates) Usually, this is what you want. However, here it causes a problem because `setTodos` does not immediately update the DOM. So the time you scroll the list to its last element, the todo has not yet been added. This is why scrolling always "lags behind" by one item.
> 
> To fix this issue, you can force React to update ("flush") the DOM synchronously. To do this, import `flushSync` from `react-dom` and **wrap the state update** into a `flushSync` call:
> 
> ```js
> flushSync(() => {
>   setTodos([ ...todos, newTodo]);
> });
> listRef.current.lastChild.scrollIntoView();
> ```
> 
> This will instruct React to update the DOM synchronously right after the code wrapped in `flushSync` executes. As a result, the last todo will already be in the DOM by the time you try to scroll to it:
> 
> [Interactive example removed — see react.dev for live demo]


## Best practices for DOM manipulation with refs {/*best-practices-for-dom-manipulation-with-refs*/}

Refs are an escape hatch. You should only use them when you have to "step outside React". Common examples of this include managing focus, scroll position, or calling browser APIs that React does not expose.

If you stick to non-destructive actions like focusing and scrolling, you shouldn't encounter any problems. However, if you try to **modify** the DOM manually, you can risk conflicting with the changes React is making.

To illustrate this problem, this example includes a welcome message and two buttons. The first button toggles its presence using [conditional rendering](/learn/conditional-rendering) and [state](/learn/state-a-components-memory), as you would usually do in React. The second button uses the [`remove()` DOM API](https://developer.mozilla.org/en-US/docs/Web/API/Element/remove) to forcefully remove it from the DOM outside of React's control.

Try pressing "Toggle with setState" a few times. The message should disappear and appear again. Then press "Remove from the DOM". This will forcefully remove it. Finally, press "Toggle with setState":

[Interactive example removed — see react.dev for live demo]


After you've manually removed the DOM element, trying to use `setState` to show it again will lead to a crash. This is because you've changed the DOM, and React doesn't know how to continue managing it correctly.

**Avoid changing DOM nodes managed by React.** Modifying, adding children to, or removing children from elements that are managed by React can lead to inconsistent visual results or crashes like above.

However, this doesn't mean that you can't do it at all. It requires caution. **You can safely modify parts of the DOM that React has _no reason_ to update.** For example, if some `<div>` is always empty in the JSX, React won't have a reason to touch its children list. Therefore, it is safe to manually add or remove elements there.

- Refs are a generic concept, but most often you'll use them to hold DOM elements.
- You instruct React to put a DOM node into `myRef.current` by passing `<div ref={myRef}>`.
- Usually, you will use refs for non-destructive actions like focusing, scrolling, or measuring DOM elements.
- A component doesn't expose its DOM nodes by default. You can opt into exposing a DOM node by using the `ref` prop.
- Avoid changing DOM nodes managed by React.
- If you do modify DOM nodes managed by React, modify parts that React has no reason to update.






# Useref

`useRef` is a React Hook that lets you reference a value that's not needed for rendering.

```js
const ref = useRef(initialValue)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useRef(initialValue)` {/*useref*/}

Call `useRef` at the top level of your component to declare a [ref.](/learn/referencing-values-with-refs)

```js
import { useRef } from 'react';

function MyComponent() {
  const intervalRef = useRef(0);
  const inputRef = useRef(null);
  // ...
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `initialValue`: The value you want the ref object's `current` property to be initially. It can be a value of any type. This argument is ignored after the initial render.

#### Returns {/*returns*/}

`useRef` returns an object with a single property:

* `current`: Initially, it's set to the `initialValue` you have passed. You can later set it to something else. If you pass the ref object to React as a `ref` attribute to a JSX node, React will set its `current` property.

On the next renders, `useRef` will return the same object.

#### Caveats {/*caveats*/}

* You can mutate the `ref.current` property. Unlike state, it is mutable. However, if it holds an object that is used for rendering (for example, a piece of your state), then you shouldn't mutate that object.
* When you change the `ref.current` property, React does not re-render your component. React is not aware of when you change it because a ref is a plain JavaScript object.
* Do not write _or read_ `ref.current` during rendering, except for [initialization.](#avoiding-recreating-the-ref-contents) This makes your component's behavior unpredictable.
* In Strict Mode, React will **call your component function twice** in order to [help you find accidental impurities.](/reference/react/useState#my-initializer-or-updater-function-runs-twice) This is development-only behavior and does not affect production. Each ref object will be created twice, but one of the versions will be discarded. If your component function is pure (as it should be), this should not affect the behavior.

---

## Usage {/*usage*/}

### Referencing a value with a ref {/*referencing-a-value-with-a-ref*/}

Call `useRef` at the top level of your component to declare one or more [refs.](/learn/referencing-values-with-refs)

```js [[1, 4, "intervalRef"], [3, 4, "0"]]
import { useRef } from 'react';

function Stopwatch() {
  const intervalRef = useRef(0);
  // ...
```

`useRef` returns a ref object with a single `current` property initially set to the initial value you provided.

On the next renders, `useRef` will return the same object. You can change its `current` property to store information and read it later. This might remind you of [state](/reference/react/useState), but there is an important difference.

**Changing a ref does not trigger a re-render.** This means refs are perfect for storing information that doesn't affect the visual output of your component. For example, if you need to store an [interval ID](https://developer.mozilla.org/en-US/docs/Web/API/setInterval) and retrieve it later, you can put it in a ref. To update the value inside the ref, you need to manually change its `current` property:

```js [[2, 5, "intervalRef.current"]]
function handleStartClick() {
  const intervalId = setInterval(() => {
    // ...
  }, 1000);
  intervalRef.current = intervalId;
}
```

Later, you can read that interval ID from the ref so that you can call [clear that interval](https://developer.mozilla.org/en-US/docs/Web/API/clearInterval):

```js [[2, 2, "intervalRef.current"]]
function handleStopClick() {
  const intervalId = intervalRef.current;
  clearInterval(intervalId);
}
```

By using a ref, you ensure that:

- You can **store information** between re-renders (unlike regular variables, which reset on every render).
- Changing it **does not trigger a re-render** (unlike state variables, which trigger a re-render).
- The **information is local** to each copy of your component (unlike the variables outside, which are shared).

Changing a ref does not trigger a re-render, so refs are not appropriate for storing information you want to display on the screen. Use state for that instead. Read more about [choosing between `useRef` and `useState`.](/learn/referencing-values-with-refs#differences-between-refs-and-state)

<Recipes titleText="Examples of referencing a value with useRef" titleId="examples-value">

#### Click counter {/*click-counter*/}

This component uses a ref to keep track of how many times the button was clicked. Note that it's okay to use a ref instead of state here because the click count is only read and written in an event handler.

[Interactive example removed — see react.dev for live demo]


If you show `{ref.current}` in the JSX, the number won't update on click. This is because setting `ref.current` does not trigger a re-render. Information that's used for rendering should be state instead.

<Solution />

#### A stopwatch {/*a-stopwatch*/}

This example uses a combination of state and refs. Both `startTime` and `now` are state variables because they are used for rendering. But we also need to hold an [interval ID](https://developer.mozilla.org/en-US/docs/Web/API/setInterval) so that we can stop the interval on button press. Since the interval ID is not used for rendering, it's appropriate to keep it in a ref, and manually update it.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

> **Pitfall:**
>
> 
> 
> **Do not write _or read_ `ref.current` during rendering.**
> 
> React expects that the body of your component [behaves like a pure function](/learn/keeping-components-pure):
> 
> - If the inputs ([props](/learn/passing-props-to-a-component), [state](/learn/state-a-components-memory), and [context](/learn/passing-data-deeply-with-context)) are the same, it should return exactly the same JSX.
> - Calling it in a different order or with different arguments should not affect the results of other calls.
> 
> Reading or writing a ref **during rendering** breaks these expectations.
> 
> ```js {expectedErrors: {'react-compiler': [4]}} {3-4,6-7}
> function MyComponent() {
>   // ...
>   // 🚩 Don't write a ref during rendering
>   myRef.current = 123;
>   // ...
>   // 🚩 Don't read a ref during rendering
>   return <h1>{myOtherRef.current}</h1>;
> }
> ```
> 
> You can read or write refs **from event handlers or effects instead**.
> 
> ```js {4-5,9-10}
> function MyComponent() {
>   // ...
>   useEffect(() => {
>     // ✅ You can read or write refs in effects
>     myRef.current = 123;
>   });
>   // ...
>   function handleClick() {
>     // ✅ You can read or write refs in event handlers
>     doSomething(myOtherRef.current);
>   }
>   // ...
> }
> ```
> 
> If you *have to* read [or write](/reference/react/useState#storing-information-from-previous-renders) something during rendering, [use state](/reference/react/useState) instead.
> 
> When you break these rules, your component might still work, but most of the newer features we're adding to React will rely on these expectations. Read more about [keeping your components pure.](/learn/keeping-components-pure#where-you-_can_-cause-side-effects)
> 
> 


---

### Manipulating the DOM with a ref {/*manipulating-the-dom-with-a-ref*/}

It's particularly common to use a ref to manipulate the [DOM.](https://developer.mozilla.org/en-US/docs/Web/API/HTML_DOM_API) React has built-in support for this.

First, declare a ref object with an initial value of `null`:

```js [[1, 4, "inputRef"], [3, 4, "null"]]
import { useRef } from 'react';

function MyComponent() {
  const inputRef = useRef(null);
  // ...
```

Then pass your ref object as the `ref` attribute to the JSX of the DOM node you want to manipulate:

```js [[1, 2, "inputRef"]]
  // ...
  return <input ref={inputRef} />;
```

After React creates the DOM node and puts it on the screen, React will set the `current` property of your ref object to that DOM node. Now you can access the `<input>`'s DOM node and call methods like [`focus()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus):

```js [[2, 2, "inputRef.current"]]
  function handleClick() {
    inputRef.current.focus();
  }
```

React will set the `current` property back to `null` when the node is removed from the screen.

Read more about [manipulating the DOM with refs.](/learn/manipulating-the-dom-with-refs)

<Recipes titleText="Examples of manipulating the DOM with useRef" titleId="examples-dom">

#### Focusing a text input {/*focusing-a-text-input*/}

In this example, clicking the button will focus the input:

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Scrolling an image into view {/*scrolling-an-image-into-view*/}

In this example, clicking the button will scroll an image into view. It uses a ref to the list DOM node, and then calls DOM [`querySelectorAll`](https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelectorAll) API to find the image we want to scroll to.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Playing and pausing a video {/*playing-and-pausing-a-video*/}

This example uses a ref to call [`play()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play) and [`pause()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause) on a `<video>` DOM node.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Exposing a ref to your own component {/*exposing-a-ref-to-your-own-component*/}

Sometimes, you may want to let the parent component manipulate the DOM inside of your component. For example, maybe you're writing a `MyInput` component, but you want the parent to be able to focus the input (which the parent has no access to). You can create a `ref` in the parent and pass the `ref` as prop to the child component. Read a [detailed walkthrough](/learn/manipulating-the-dom-with-refs#accessing-another-components-dom-nodes) here.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Avoiding recreating the ref contents {/*avoiding-recreating-the-ref-contents*/}

React saves the initial ref value once and ignores it on the next renders.

```js
function Video() {
  const playerRef = useRef(new VideoPlayer());
  // ...
```

Although the result of `new VideoPlayer()` is only used for the initial render, you're still calling this function on every render. This can be wasteful if it's creating expensive objects.

To solve it, you may initialize the ref like this instead:

```js
function Video() {
  const playerRef = useRef(null);
  if (playerRef.current === null) {
    playerRef.current = new VideoPlayer();
  }
  // ...
```

Normally, writing or reading `ref.current` during render is not allowed. However, it's fine in this case because the result is always the same, and the condition only executes during initialization so it's fully predictable.

> **Deep Dive: How to avoid null checks when initializing useRef later {/*how-to-avoid-null-checks-when-initializing-use-ref-later*/}**
>
> If you use a type checker and don't want to always check for `null`, you can try a pattern like this instead:
> 
> ```js
> function Video() {
>   const playerRef = useRef(null);
> 
>   function getPlayer() {
>     if (playerRef.current !== null) {
>       return playerRef.current;
>     }
>     const player = new VideoPlayer();
>     playerRef.current = player;
>     return player;
>   }
> 
>   // ...
> ```
> 
> Here, the `playerRef` itself is nullable. However, you should be able to convince your type checker that there is no case in which `getPlayer()` returns `null`. Then use `getPlayer()` in your event handlers.


---

## Troubleshooting {/*troubleshooting*/}

### I can't get a ref to a custom component {/*i-cant-get-a-ref-to-a-custom-component*/}

If you try to pass a `ref` to your own component like this:

```js
const inputRef = useRef(null);

return <MyInput ref={inputRef} />;
```

You might get an error in the console:

<ConsoleBlock level="error">

TypeError: Cannot read properties of null

</ConsoleBlock>

By default, your own components don't expose refs to the DOM nodes inside them.

To fix this, find the component that you want to get a ref to:

```js
export default function MyInput({ value, onChange }) {
  return (
    <input
      value={value}
      onChange={onChange}
    />
  );
}
```

And then add `ref` to the list of props your component accepts and pass `ref` as a prop to the relevant child [built-in component](/reference/react-dom/components/common) like this:

```js {1,6}
function MyInput({ value, onChange, ref }) {
  return (
    <input
      value={value}
      onChange={onChange}
      ref={ref}
    />
  );
};

export default MyInput;
```

Then the parent component can get a ref to it.

Read more about [accessing another component's DOM nodes.](/learn/manipulating-the-dom-with-refs#accessing-another-components-dom-nodes)


# Useimperativehandle

`useImperativeHandle` is a React Hook that lets you customize the handle exposed as a [ref.](/learn/manipulating-the-dom-with-refs)

```js
useImperativeHandle(ref, createHandle, dependencies?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useImperativeHandle(ref, createHandle, dependencies?)` {/*useimperativehandle*/}

Call `useImperativeHandle` at the top level of your component to customize the ref handle it exposes:

```js
import { useImperativeHandle } from 'react';

function MyInput({ ref }) {
  useImperativeHandle(ref, () => {
    return {
      // ... your methods ...
    };
  }, []);
  // ...
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `ref`: The `ref` you received as a prop to the `MyInput` component.

* `createHandle`: A function that takes no arguments and returns the ref handle you want to expose. That ref handle can have any type. Usually, you will return an object with the methods you want to expose.

* **optional** `dependencies`: The list of all reactive values referenced inside of the `createHandle` code. Reactive values include props, state, and all the variables and functions declared directly inside your component body. If your linter is [configured for React](/learn/editor-setup#linting), it will verify that every reactive value is correctly specified as a dependency. The list of dependencies must have a constant number of items and be written inline like `[dep1, dep2, dep3]`. React will compare each dependency with its previous value using the [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison. If a re-render resulted in a change to some dependency, or if you omitted this argument, your `createHandle` function will re-execute, and the newly created handle will be assigned to the ref.

> **Note:**
>
> 
> 
> Starting with React 19, [`ref` is available as a prop.](/blog/2024/12/05/react-19#ref-as-a-prop) In React 18 and earlier, it was necessary to get the `ref` from [`forwardRef`.](/reference/react/forwardRef) 
> 
> 


#### Returns {/*returns*/}

`useImperativeHandle` returns `undefined`.

---

## Usage {/*usage*/}

### Exposing a custom ref handle to the parent component {/*exposing-a-custom-ref-handle-to-the-parent-component*/}

To expose a DOM node to the parent element, pass in the `ref` prop to the node.

```js {2}
function MyInput({ ref }) {
  return <input ref={ref} />;
};
```

With the code above, [a ref to `MyInput` will receive the `<input>` DOM node.](/learn/manipulating-the-dom-with-refs) However, you can expose a custom value instead. To customize the exposed handle, call `useImperativeHandle` at the top level of your component:

```js {4-8}
import { useImperativeHandle } from 'react';

function MyInput({ ref }) {
  useImperativeHandle(ref, () => {
    return {
      // ... your methods ...
    };
  }, []);

  return <input />;
};
```

Note that in the code above, the `ref` is no longer passed to the `<input>`.

For example, suppose you don't want to expose the entire `<input>` DOM node, but you want to expose two of its methods: `focus` and `scrollIntoView`. To do this, keep the real browser DOM in a separate ref. Then use `useImperativeHandle` to expose a handle with only the methods that you want the parent component to call:

```js {7-14}
import { useRef, useImperativeHandle } from 'react';

function MyInput({ ref }) {
  const inputRef = useRef(null);

  useImperativeHandle(ref, () => {
    return {
      focus() {
        inputRef.current.focus();
      },
      scrollIntoView() {
        inputRef.current.scrollIntoView();
      },
    };
  }, []);

  return <input ref={inputRef} />;
};
```

Now, if the parent component gets a ref to `MyInput`, it will be able to call the `focus` and `scrollIntoView` methods on it. However, it will not have full access to the underlying `<input>` DOM node.

[Interactive example removed — see react.dev for live demo]


---

### Exposing your own imperative methods {/*exposing-your-own-imperative-methods*/}

The methods you expose via an imperative handle don't have to match the DOM methods exactly. For example, this `Post` component exposes a `scrollAndFocusAddComment` method via an imperative handle. This lets the parent `Page` scroll the list of comments *and* focus the input field when you click the button:

[Interactive example removed — see react.dev for live demo]


> **Pitfall:**
>
> 
> 
> **Do not overuse refs.** You should only use refs for *imperative* behaviors that you can't express as props: for example, scrolling to a node, focusing a node, triggering an animation, selecting text, and so on.
> 
> **If you can express something as a prop, you should not use a ref.** For example, instead of exposing an imperative handle like `{ open, close }` from a `Modal` component, it is better to take `isOpen` as a prop like `<Modal isOpen={isOpen} />`. [Effects](/learn/synchronizing-with-effects) can help you expose imperative behaviors via props.
> 
> 



# Forwardref

<Deprecated>

In React 19, `forwardRef` is no longer necessary. Pass `ref` as a prop instead.

`forwardRef` will be deprecated in a future release. Learn more [here](/blog/2024/04/25/react-19#ref-as-a-prop).

</Deprecated>

`forwardRef` lets your component expose a DOM node to the parent component with a [ref.](/learn/manipulating-the-dom-with-refs)

```js
const SomeComponent = forwardRef(render)
```

<InlineToc />

---

## Reference {/*reference*/}

### `forwardRef(render)` {/*forwardref*/}

Call `forwardRef()` to let your component receive a ref and forward it to a child component:

```js
import { forwardRef } from 'react';

const MyInput = forwardRef(function MyInput(props, ref) {
  // ...
});
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `render`: The render function for your component. React calls this function with the props and `ref` that your component received from its parent. The JSX you return will be the output of your component.

#### Returns {/*returns*/}

`forwardRef` returns a React component that you can render in JSX. Unlike React components defined as plain functions, a component returned by `forwardRef` is also able to receive a `ref` prop.

#### Caveats {/*caveats*/}

* In Strict Mode, React will **call your render function twice** in order to [help you find accidental impurities.](/reference/react/useState#my-initializer-or-updater-function-runs-twice) This is development-only behavior and does not affect production. If your render function is pure (as it should be), this should not affect the logic of your component. The result from one of the calls will be ignored.


---

### `render` function {/*render-function*/}

`forwardRef` accepts a render function as an argument. React calls this function with `props` and `ref`:

```js
const MyInput = forwardRef(function MyInput(props, ref) {
  return (
    <label>
      {props.label}
      <input ref={ref} />
    </label>
  );
});
```

#### Parameters {/*render-parameters*/}

* `props`: The props passed by the parent component.

* `ref`:  The `ref` attribute passed by the parent component. The `ref` can be an object or a function. If the parent component has not passed a ref, it will be `null`. You should either pass the `ref` you receive to another component, or pass it to [`useImperativeHandle`.](/reference/react/useImperativeHandle)

#### Returns {/*render-returns*/}

`forwardRef` returns a React component that you can render in JSX. Unlike React components defined as plain functions, the component returned by `forwardRef` is able to take a `ref` prop.

---

## Usage {/*usage*/}

### Exposing a DOM node to the parent component {/*exposing-a-dom-node-to-the-parent-component*/}

By default, each component's DOM nodes are private. However, sometimes it's useful to expose a DOM node to the parent--for example, to allow focusing it. To opt in, wrap your component definition into `forwardRef()`:

```js {3,11}
import { forwardRef } from 'react';

const MyInput = forwardRef(function MyInput(props, ref) {
  const { label, ...otherProps } = props;
  return (
    <label>
      {label}
      <input {...otherProps} />
    </label>
  );
});
```

You will receive a ref as the second argument after props. Pass it to the DOM node that you want to expose:

```js {8} [[1, 3, "ref"], [1, 8, "ref", 30]]
import { forwardRef } from 'react';

const MyInput = forwardRef(function MyInput(props, ref) {
  const { label, ...otherProps } = props;
  return (
    <label>
      {label}
      <input {...otherProps} ref={ref} />
    </label>
  );
});
```

This lets the parent `Form` component access the `<input>` DOM node exposed by `MyInput`:

```js [[1, 2, "ref"], [1, 10, "ref", 41], [2, 5, "ref.current"]]
function Form() {
  const ref = useRef(null);

  function handleClick() {
    ref.current.focus();
  }

  return (
    <form>
      <MyInput label="Enter your name:" ref={ref} />
      <button type="button" onClick={handleClick}>
        Edit
      </button>
    </form>
  );
}
```

This `Form` component [passes a ref](/reference/react/useRef#manipulating-the-dom-with-a-ref) to `MyInput`. The `MyInput` component *forwards* that ref to the `<input>` browser tag. As a result, the `Form` component can access that `<input>` DOM node and call [`focus()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) on it.

Keep in mind that exposing a ref to the DOM node inside your component makes it harder to change your component's internals later. You will typically expose DOM nodes from reusable low-level components like buttons or text inputs, but you won't do it for application-level components like an avatar or a comment.

<Recipes titleText="Examples of forwarding a ref">

#### Focusing a text input {/*focusing-a-text-input*/}

Clicking the button will focus the input. The `Form` component defines a ref and passes it to the `MyInput` component. The `MyInput` component forwards that ref to the browser `<input>`. This lets the `Form` component focus the `<input>`.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Playing and pausing a video {/*playing-and-pausing-a-video*/}

Clicking the button will call [`play()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/play) and [`pause()`](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/pause) on a `<video>` DOM node. The `App` component defines a ref and passes it to the `MyVideoPlayer` component. The `MyVideoPlayer` component forwards that ref to the browser `<video>` node. This lets the `App` component play and pause the `<video>`.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Forwarding a ref through multiple components {/*forwarding-a-ref-through-multiple-components*/}

Instead of forwarding a `ref` to a DOM node, you can forward it to your own component like `MyInput`:

```js {1,5}
const FormField = forwardRef(function FormField(props, ref) {
  // ...
  return (
    <>
      <MyInput ref={ref} />
      ...
    </>
  );
});
```

If that `MyInput` component forwards a ref to its `<input>`, a ref to `FormField` will give you that `<input>`:

```js {2,5,10}
function Form() {
  const ref = useRef(null);

  function handleClick() {
    ref.current.focus();
  }

  return (
    <form>
      <FormField label="Enter your name:" ref={ref} isRequired={true} />
      <button type="button" onClick={handleClick}>
        Edit
      </button>
    </form>
  );
}
```

The `Form` component defines a ref and passes it to `FormField`. The `FormField` component forwards that ref to `MyInput`, which forwards it to a browser `<input>` DOM node. This is how `Form` accesses that DOM node.


[Interactive example removed — see react.dev for live demo]


---

### Exposing an imperative handle instead of a DOM node {/*exposing-an-imperative-handle-instead-of-a-dom-node*/}

Instead of exposing an entire DOM node, you can expose a custom object, called an *imperative handle,* with a more constrained set of methods. To do this, you'd need to define a separate ref to hold the DOM node:

```js {2,6}
const MyInput = forwardRef(function MyInput(props, ref) {
  const inputRef = useRef(null);

  // ...

  return <input {...props} ref={inputRef} />;
});
```

Pass the `ref` you received to [`useImperativeHandle`](/reference/react/useImperativeHandle) and specify the value you want to expose to the `ref`:

```js {6-15}
import { forwardRef, useRef, useImperativeHandle } from 'react';

const MyInput = forwardRef(function MyInput(props, ref) {
  const inputRef = useRef(null);

  useImperativeHandle(ref, () => {
    return {
      focus() {
        inputRef.current.focus();
      },
      scrollIntoView() {
        inputRef.current.scrollIntoView();
      },
    };
  }, []);

  return <input {...props} ref={inputRef} />;
});
```

If some component gets a ref to `MyInput`, it will only receive your `{ focus, scrollIntoView }` object instead of the DOM node. This lets you limit the information you expose about your DOM node to the minimum.

[Interactive example removed — see react.dev for live demo]


[Read more about using imperative handles.](/reference/react/useImperativeHandle)

> **Pitfall:**
>
> 
> 
> **Do not overuse refs.** You should only use refs for *imperative* behaviors that you can't express as props: for example, scrolling to a node, focusing a node, triggering an animation, selecting text, and so on.
> 
> **If you can express something as a prop, you should not use a ref.** For example, instead of exposing an imperative handle like `{ open, close }` from a `Modal` component, it is better to take `isOpen` as a prop like `<Modal isOpen={isOpen} />`. [Effects](/learn/synchronizing-with-effects) can help you expose imperative behaviors via props.
> 
> 


---

## Troubleshooting {/*troubleshooting*/}

### My component is wrapped in `forwardRef`, but the `ref` to it is always `null` {/*my-component-is-wrapped-in-forwardref-but-the-ref-to-it-is-always-null*/}

This usually means that you forgot to actually use the `ref` that you received.

For example, this component doesn't do anything with its `ref`:

```js {1}
const MyInput = forwardRef(function MyInput({ label }, ref) {
  return (
    <label>
      {label}
      <input />
    </label>
  );
});
```

To fix it, pass the `ref` down to a DOM node or another component that can accept a ref:

```js {1,5}
const MyInput = forwardRef(function MyInput({ label }, ref) {
  return (
    <label>
      {label}
      <input ref={ref} />
    </label>
  );
});
```

The `ref` to `MyInput` could also be `null` if some of the logic is conditional:

```js {1,5}
const MyInput = forwardRef(function MyInput({ label, showInput }, ref) {
  return (
    <label>
      {label}
      {showInput && <input ref={ref} />}
    </label>
  );
});
```

If `showInput` is `false`, then the ref won't be forwarded to any node, and a ref to `MyInput` will remain empty. This is particularly easy to miss if the condition is hidden inside another component, like `Panel` in this example:

```js {5,7}
const MyInput = forwardRef(function MyInput({ label, showInput }, ref) {
  return (
    <label>
      {label}
      <Panel isExpanded={showInput}>
        <input ref={ref} />
      </Panel>
    </label>
  );
});
```


# Createportal

`createPortal` lets you render some children into a different part of the DOM.


```js
<div>
  <SomeComponent />
  {createPortal(children, domNode, key?)}
</div>
```

<InlineToc />

---

## Reference {/*reference*/}

### `createPortal(children, domNode, key?)` {/*createportal*/}

To create a portal, call `createPortal`, passing some JSX, and the DOM node where it should be rendered:

```js
import { createPortal } from 'react-dom';

// ...

<div>
  <p>This child is placed in the parent div.</p>
  {createPortal(
    <p>This child is placed in the document body.</p>,
    document.body
  )}
</div>
```

[See more examples below.](#usage)

A portal only changes the physical placement of the DOM node. In every other way, the JSX you render into a portal acts as a child node of the React component that renders it. For example, the child can access the context provided by the parent tree, and events bubble up from children to parents according to the React tree.

#### Parameters {/*parameters*/}

* `children`: Anything that can be rendered with React, such as a piece of JSX (e.g. `<div />` or `<SomeComponent />`), a [Fragment](/reference/react/Fragment) (`<>...</>`), a string or a number, or an array of these.

* `domNode`: Some DOM node, such as those returned by `document.getElementById()`. The node must already exist. Passing a different DOM node during an update will cause the portal content to be recreated.

* **optional** `key`: A unique string or number to be used as the portal's [key.](/learn/rendering-lists#keeping-list-items-in-order-with-key)

#### Returns {/*returns*/}

`createPortal` returns a React node that can be included into JSX or returned from a React component. If React encounters it in the render output, it will place the provided `children` inside the provided `domNode`.

#### Caveats {/*caveats*/}

* Events from portals propagate according to the React tree rather than the DOM tree. For example, if you click inside a portal, and the portal is wrapped in `<div onClick>`, that `onClick` handler will fire. If this causes issues, either stop the event propagation from inside the portal, or move the portal itself up in the React tree.

---

## Usage {/*usage*/}

### Rendering to a different part of the DOM {/*rendering-to-a-different-part-of-the-dom*/}

*Portals* let your components render some of their children into a different place in the DOM. This lets a part of your component "escape" from whatever containers it may be in. For example, a component can display a modal dialog or a tooltip that appears above and outside of the rest of the page.

To create a portal, render the result of `createPortal` with some JSX and the DOM node where it should go:

```js [[1, 8, "<p>This child is placed in the document body.</p>"], [2, 9, "document.body"]]
import { createPortal } from 'react-dom';

function MyComponent() {
  return (
    <div style={{ border: '2px solid black' }}>
      <p>This child is placed in the parent div.</p>
      {createPortal(
        <p>This child is placed in the document body.</p>,
        document.body
      )}
    </div>
  );
}
```

React will put the DOM nodes for the JSX you passed inside of the DOM node you provided.

Without a portal, the second `<p>` would be placed inside the parent `<div>`, but the portal "teleported" it into the [`document.body`:](https://developer.mozilla.org/en-US/docs/Web/API/Document/body)

[Interactive example removed — see react.dev for live demo]


Notice how the second paragraph visually appears outside the parent `<div>` with the border. If you inspect the DOM structure with developer tools, you'll see that the second `<p>` got placed directly into the `<body>`:

```html {4-6,9}
<body>
  <div id="root">
    ...
      <div style="border: 2px solid black">
        <p>This child is placed inside the parent div.</p>
      </div>
    ...
  </div>
  <p>This child is placed in the document body.</p>
</body>
```

A portal only changes the physical placement of the DOM node. In every other way, the JSX you render into a portal acts as a child node of the React component that renders it. For example, the child can access the context provided by the parent tree, and events still bubble up from children to parents according to the React tree.

---

### Rendering a modal dialog with a portal {/*rendering-a-modal-dialog-with-a-portal*/}

You can use a portal to create a modal dialog that floats above the rest of the page, even if the component that summons the dialog is inside a container with `overflow: hidden` or other styles that interfere with the dialog.

In this example, the two containers have styles that disrupt the modal dialog, but the one rendered into a portal is unaffected because, in the DOM, the modal is not contained within the parent JSX elements.

[Interactive example removed — see react.dev for live demo]


> **Pitfall:**
>
> 
> 
> It's important to make sure that your app is accessible when using portals. For instance, you may need to manage keyboard focus so that the user can move the focus in and out of the portal in a natural way.
> 
> Follow the [WAI-ARIA Modal Authoring Practices](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal) when creating modals. If you use a community package, ensure that it is accessible and follows these guidelines.
> 
> 


---

### Rendering React components into non-React server markup {/*rendering-react-components-into-non-react-server-markup*/}

Portals can be useful if your React root is only part of a static or server-rendered page that isn't built with React. For example, if your page is built with a server framework like Rails, you can create areas of interactivity within static areas such as sidebars. Compared with having [multiple separate React roots,](/reference/react-dom/client/createRoot#rendering-a-page-partially-built-with-react) portals let you treat the app as a single React tree with shared state even though its parts render to different parts of the DOM.

[Interactive example removed — see react.dev for live demo]


---

### Rendering React components into non-React DOM nodes {/*rendering-react-components-into-non-react-dom-nodes*/}

You can also use a portal to manage the content of a DOM node that's managed outside of React. For example, suppose you're integrating with a non-React map widget and you want to render React content inside a popup. To do this, declare a `popupContainer` state variable to store the DOM node you're going to render into:

```js
const [popupContainer, setPopupContainer] = useState(null);
```

When you create the third-party widget, store the DOM node returned by the widget so you can render into it:

```js {5-6}
useEffect(() => {
  if (mapRef.current === null) {
    const map = createMapWidget(containerRef.current);
    mapRef.current = map;
    const popupDiv = addPopupToMapWidget(map);
    setPopupContainer(popupDiv);
  }
}, []);
```

This lets you use `createPortal` to render React content into `popupContainer` once it becomes available:

```js {3-6}
return (
  <div style={{ width: 250, height: 250 }} ref={containerRef}>
    {popupContainer !== null && createPortal(
      <p>Hello from React!</p>,
      popupContainer
    )}
  </div>
);
```

Here is a complete example you can play with:

[Interactive example removed — see react.dev for live demo]



# Flushsync

> **Pitfall:**
>
> 
> 
> Using `flushSync` is uncommon and can hurt the performance of your app.
> 
> 


`flushSync` lets you force React to flush any updates inside the provided callback synchronously. This ensures that the DOM is updated immediately.

```js
flushSync(callback)
```

<InlineToc />

---

## Reference {/*reference*/}

### `flushSync(callback)` {/*flushsync*/}

Call `flushSync` to force React to flush any pending work and update the DOM synchronously.

```js
import { flushSync } from 'react-dom';

flushSync(() => {
  setSomething(123);
});
```

Most of the time, `flushSync` can be avoided. Use `flushSync` as last resort.

[See more examples below.](#usage)

#### Parameters {/*parameters*/}


* `callback`: A function. React will immediately call this callback and flush any updates it contains synchronously. It may also flush any pending updates, or Effects, or updates inside of Effects. If an update suspends as a result of this `flushSync` call, the fallbacks may be re-shown.

#### Returns {/*returns*/}

`flushSync` returns `undefined`.

#### Caveats {/*caveats*/}

* `flushSync` can significantly hurt performance. Use sparingly.
* `flushSync` may force pending Suspense boundaries to show their `fallback` state.
* `flushSync` may run pending Effects and synchronously apply any updates they contain before returning.
* `flushSync` may flush updates outside the callback when necessary to flush the updates inside the callback. For example, if there are pending updates from a click, React may flush those before flushing the updates inside the callback.

---

## Usage {/*usage*/}

### Flushing updates for third-party integrations {/*flushing-updates-for-third-party-integrations*/}

When integrating with third-party code such as browser APIs or UI libraries, it may be necessary to force React to flush updates. Use `flushSync` to force React to flush any state updates inside the callback synchronously:

```js [[1, 2, "setSomething(123)"]]
flushSync(() => {
  setSomething(123);
});
// By this line, the DOM is updated.
```

This ensures that, by the time the next line of code runs, React has already updated the DOM.

**Using `flushSync` is uncommon, and using it often can significantly hurt the performance of your app.** If your app only uses React APIs, and does not integrate with third-party libraries, `flushSync` should be unnecessary.

However, it can be helpful for integrating with third-party code like browser APIs.

Some browser APIs expect results inside of callbacks to be written to the DOM synchronously, by the end of the callback, so the browser can do something with the rendered DOM. In most cases, React handles this for you automatically. But in some cases it may be necessary to force a synchronous update.

For example, the browser `onbeforeprint` API allows you to change the page immediately before the print dialog opens. This is useful for applying custom print styles that allow the document to display better for printing. In the example below, you use `flushSync` inside of the `onbeforeprint` callback to immediately "flush" the React state to the DOM. Then, by the time the print dialog opens, `isPrinting` displays "yes":

[Interactive example removed — see react.dev for live demo]


Without `flushSync`, the print dialog will display `isPrinting` as "no". This is because React batches the updates asynchronously and the print dialog is displayed before the state is updated.

> **Pitfall:**
>
> 
> 
> `flushSync` can significantly hurt performance, and may unexpectedly force pending Suspense boundaries to show their fallback state.
> 
> Most of the time, `flushSync` can be avoided, so use `flushSync` as a last resort.
> 
> 


---

## Troubleshooting {/*troubleshooting*/}

### I'm getting an error: "flushSync was called from inside a lifecycle method" {/*im-getting-an-error-flushsync-was-called-from-inside-a-lifecycle-method*/}


React cannot `flushSync` in the middle of a render. If you do, it will noop and warn:

<ConsoleBlock level="error">

Warning: flushSync was called from inside a lifecycle method. React cannot flush when React is already rendering. Consider moving this call to a scheduler task or micro task.

</ConsoleBlock>

This includes calling `flushSync` inside:

- rendering a component.
- `useLayoutEffect` or `useEffect` hooks.
- Class component lifecycle methods.

For example, calling `flushSync` in an Effect will noop and warn:

```js
import { useEffect } from 'react';
import { flushSync } from 'react-dom';

function MyComponent() {
  useEffect(() => {
    // 🚩 Wrong: calling flushSync inside an effect
    flushSync(() => {
      setSomething(newValue);
    });
  }, []);

  return <div>{/* ... */}</div>;
}
```

To fix this, you usually want to move the `flushSync` call to an event:

```js
function handleClick() {
  // ✅ Correct: flushSync in event handlers is safe
  flushSync(() => {
    setSomething(newValue);
  });
}
```


If it's difficult to move to an event, you can defer `flushSync` in a microtask:

```js {3,7}
useEffect(() => {
  // ✅ Correct: defer flushSync to a microtask
  queueMicrotask(() => {
    flushSync(() => {
      setSomething(newValue);
    });
  });
}, []);
```

This will allow the current render to finish and schedule another syncronous render to flush the updates.

> **Pitfall:**
>
> 
> 
> `flushSync` can significantly hurt performance, but this particular pattern is even worse for performance. Exhaust all other options before calling `flushSync` in a microtask as an escape hatch.
> 
> 

