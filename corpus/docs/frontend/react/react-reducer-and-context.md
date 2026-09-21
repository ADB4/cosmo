---
title: React Reducer And Context
source: react.dev
syllabus_weeks: [6]
topics: [useReducer, reducer, dispatch, Context, useContext, createContext, state management, scaling state]
---



# Extracting State Logic Into A Reducer

Components with many state updates spread across many event handlers can get overwhelming. For these cases, you can consolidate all the state update logic outside your component in a single function, called a _reducer._

- What a reducer function is
- How to refactor `useState` to `useReducer`
- When to use a reducer
- How to write one well

## Consolidate state logic with a reducer {/*consolidate-state-logic-with-a-reducer*/}

As your components grow in complexity, it can get harder to see at a glance all the different ways in which a component's state gets updated. For example, the `TaskApp` component below holds an array of `tasks` in state and uses three different event handlers to add, remove, and edit tasks:

[Interactive example removed — see react.dev for live demo]


Each of its event handlers calls `setTasks` in order to update the state. As this component grows, so does the amount of state logic sprinkled throughout it. To reduce this complexity and keep all your logic in one easy-to-access place, you can move that state logic into a single function outside your component, **called a "reducer".**

Reducers are a different way to handle state. You can migrate from `useState` to `useReducer` in three steps:

1. **Move** from setting state to dispatching actions.
2. **Write** a reducer function.
3. **Use** the reducer from your component.

### Step 1: Move from setting state to dispatching actions {/*step-1-move-from-setting-state-to-dispatching-actions*/}

Your event handlers currently specify _what to do_ by setting state:

```js
function handleAddTask(text) {
  setTasks([
    ...tasks,
    {
      id: nextId++,
      text: text,
      done: false,
    },
  ]);
}

function handleChangeTask(task) {
  setTasks(
    tasks.map((t) => {
      if (t.id === task.id) {
        return task;
      } else {
        return t;
      }
    })
  );
}

function handleDeleteTask(taskId) {
  setTasks(tasks.filter((t) => t.id !== taskId));
}
```

Remove all the state setting logic. What you are left with are three event handlers:

- `handleAddTask(text)` is called when the user presses "Add".
- `handleChangeTask(task)` is called when the user toggles a task or presses "Save".
- `handleDeleteTask(taskId)` is called when the user presses "Delete".

Managing state with reducers is slightly different from directly setting state. Instead of telling React "what to do" by setting state, you specify "what the user just did" by dispatching "actions" from your event handlers. (The state update logic will live elsewhere!) So instead of "setting `tasks`" via an event handler, you're dispatching an "added/changed/deleted a task" action. This is more descriptive of the user's intent.

```js
function handleAddTask(text) {
  dispatch({
    type: 'added',
    id: nextId++,
    text: text,
  });
}

function handleChangeTask(task) {
  dispatch({
    type: 'changed',
    task: task,
  });
}

function handleDeleteTask(taskId) {
  dispatch({
    type: 'deleted',
    id: taskId,
  });
}
```

The object you pass to `dispatch` is called an "action":

```js {3-7}
function handleDeleteTask(taskId) {
  dispatch(
    // "action" object:
    {
      type: 'deleted',
      id: taskId,
    }
  );
}
```

It is a regular JavaScript object. You decide what to put in it, but generally it should contain the minimal information about _what happened_. (You will add the `dispatch` function itself in a later step.)

> **Note:**
>
> 
> 
> An action object can have any shape.
> 
> By convention, it is common to give it a string `type` that describes what happened, and pass any additional information in other fields. The `type` is specific to a component, so in this example either `'added'` or `'added_task'` would be fine. Choose a name that says what happened!
> 
> ```js
> dispatch({
>   // specific to component
>   type: 'what_happened',
>   // other fields go here
> });
> ```
> 
> 


### Step 2: Write a reducer function {/*step-2-write-a-reducer-function*/}

A reducer function is where you will put your state logic. It takes two arguments, the current state and the action object, and it returns the next state:

```js
function yourReducer(state, action) {
  // return next state for React to set
}
```

React will set the state to what you return from the reducer.

To move your state setting logic from your event handlers to a reducer function in this example, you will:

1. Declare the current state (`tasks`) as the first argument.
2. Declare the `action` object as the second argument.
3. Return the _next_ state from the reducer (which React will set the state to).

Here is all the state setting logic migrated to a reducer function:

```js
function tasksReducer(tasks, action) {
  if (action.type === 'added') {
    return [
      ...tasks,
      {
        id: action.id,
        text: action.text,
        done: false,
      },
    ];
  } else if (action.type === 'changed') {
    return tasks.map((t) => {
      if (t.id === action.task.id) {
        return action.task;
      } else {
        return t;
      }
    });
  } else if (action.type === 'deleted') {
    return tasks.filter((t) => t.id !== action.id);
  } else {
    throw Error('Unknown action: ' + action.type);
  }
}
```

Because the reducer function takes state (`tasks`) as an argument, you can **declare it outside of your component.** This decreases the indentation level and can make your code easier to read.

> **Note:**
>
> 
> 
> The code above uses if/else statements, but it's a convention to use [switch statements](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Statements/switch) inside reducers. The result is the same, but it can be easier to read switch statements at a glance.
> 
> We'll be using them throughout the rest of this documentation like so:
> 
> ```js
> function tasksReducer(tasks, action) {
>   switch (action.type) {
>     case 'added': {
>       return [
>         ...tasks,
>         {
>           id: action.id,
>           text: action.text,
>           done: false,
>         },
>       ];
>     }
>     case 'changed': {
>       return tasks.map((t) => {
>         if (t.id === action.task.id) {
>           return action.task;
>         } else {
>           return t;
>         }
>       });
>     }
>     case 'deleted': {
>       return tasks.filter((t) => t.id !== action.id);
>     }
>     default: {
>       throw Error('Unknown action: ' + action.type);
>     }
>   }
> }
> ```
> 
> We recommend wrapping each `case` block into the `{` and `}` curly braces so that variables declared inside of different `case`s don't clash with each other. Also, a `case` should usually end with a `return`. If you forget to `return`, the code will "fall through" to the next `case`, which can lead to mistakes!
> 
> If you're not yet comfortable with switch statements, using if/else is completely fine.
> 
> 


> **Deep Dive: Why are reducers called this way? {/*why-are-reducers-called-this-way*/}**
>
> Although reducers can "reduce" the amount of code inside your component, they are actually named after the [`reduce()`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/Reduce) operation that you can perform on arrays.
> 
> The `reduce()` operation lets you take an array and "accumulate" a single value out of many:
> 
> ```
> const arr = [1, 2, 3, 4, 5];
> const sum = arr.reduce(
>   (result, number) => result + number
> ); // 1 + 2 + 3 + 4 + 5
> ```
> 
> The function you pass to `reduce` is known as a "reducer". It takes the _result so far_ and the _current item,_ then it returns the _next result._ React reducers are an example of the same idea: they take the _state so far_ and the _action_, and return the _next state._ In this way, they accumulate actions over time into state.
> 
> You could even use the `reduce()` method with an `initialState` and an array of `actions` to calculate the final state by passing your reducer function to it:
> 
> [Interactive example removed — see react.dev for live demo]
> 
> 
> You probably won't need to do this yourself, but this is similar to what React does!


### Step 3: Use the reducer from your component {/*step-3-use-the-reducer-from-your-component*/}

Finally, you need to hook up the `tasksReducer` to your component. Import the `useReducer` Hook from React:

```js
import { useReducer } from 'react';
```

Then you can replace `useState`:

```js
const [tasks, setTasks] = useState(initialTasks);
```

with `useReducer` like so:

```js
const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
```

The `useReducer` Hook is similar to `useState`—you must pass it an initial state and it returns a stateful value and a way to set state (in this case, the dispatch function). But it's a little different.

The `useReducer` Hook takes two arguments:

1. A reducer function
2. An initial state

And it returns:

1. A stateful value
2. A dispatch function (to "dispatch" user actions to the reducer)

Now it's fully wired up! Here, the reducer is declared at the bottom of the component file:

[Interactive example removed — see react.dev for live demo]


If you want, you can even move the reducer to a different file:

[Interactive example removed — see react.dev for live demo]


Component logic can be easier to read when you separate concerns like this. Now the event handlers only specify _what happened_ by dispatching actions, and the reducer function determines _how the state updates_ in response to them.

## Comparing `useState` and `useReducer` {/*comparing-usestate-and-usereducer*/}

Reducers are not without downsides! Here's a few ways you can compare them:

- **Code size:** Generally, with `useState` you have to write less code upfront. With `useReducer`, you have to write both a reducer function _and_ dispatch actions. However, `useReducer` can help cut down on the code if many event handlers modify state in a similar way.
- **Readability:** `useState` is very easy to read when the state updates are simple. When they get more complex, they can bloat your component's code and make it difficult to scan. In this case, `useReducer` lets you cleanly separate the _how_ of update logic from the _what happened_ of event handlers.
- **Debugging:** When you have a bug with `useState`, it can be difficult to tell _where_ the state was set incorrectly, and _why_. With `useReducer`, you can add a console log into your reducer to see every state update, and _why_ it happened (due to which `action`). If each `action` is correct, you'll know that the mistake is in the reducer logic itself. However, you have to step through more code than with `useState`.
- **Testing:** A reducer is a pure function that doesn't depend on your component. This means that you can export and test it separately in isolation. While generally it's best to test components in a more realistic environment, for complex state update logic it can be useful to assert that your reducer returns a particular state for a particular initial state and action.
- **Personal preference:** Some people like reducers, others don't. That's okay. It's a matter of preference. You can always convert between `useState` and `useReducer` back and forth: they are equivalent!

We recommend using a reducer if you often encounter bugs due to incorrect state updates in some component, and want to introduce more structure to its code. You don't have to use reducers for everything: feel free to mix and match! You can even `useState` and `useReducer` in the same component.

## Writing reducers well {/*writing-reducers-well*/}

Keep these two tips in mind when writing reducers:

- **Reducers must be pure.** Similar to [state updater functions](/learn/queueing-a-series-of-state-updates), reducers run during rendering! (Actions are queued until the next render.) This means that reducers [must be pure](/learn/keeping-components-pure)—same inputs always result in the same output. They should not send requests, schedule timeouts, or perform any side effects (operations that impact things outside the component). They should update [objects](/learn/updating-objects-in-state) and [arrays](/learn/updating-arrays-in-state) without mutations.
- **Each action describes a single user interaction, even if that leads to multiple changes in the data.** For example, if a user presses "Reset" on a form with five fields managed by a reducer, it makes more sense to dispatch one `reset_form` action rather than five separate `set_field` actions. If you log every action in a reducer, that log should be clear enough for you to reconstruct what interactions or responses happened in what order. This helps with debugging!

## Writing concise reducers with Immer {/*writing-concise-reducers-with-immer*/}

Just like with [updating objects](/learn/updating-objects-in-state#write-concise-update-logic-with-immer) and [arrays](/learn/updating-arrays-in-state#write-concise-update-logic-with-immer) in regular state, you can use the Immer library to make reducers more concise. Here, [`useImmerReducer`](https://github.com/immerjs/use-immer#useimmerreducer) lets you mutate the state with `push` or `arr[i] =` assignment:

[Interactive example removed — see react.dev for live demo]


Reducers must be pure, so they shouldn't mutate state. But Immer provides you with a special `draft` object which is safe to mutate. Under the hood, Immer will create a copy of your state with the changes you made to the `draft`. This is why reducers managed by `useImmerReducer` can mutate their first argument and don't need to return state.

- To convert from `useState` to `useReducer`:
  1. Dispatch actions from event handlers.
  2. Write a reducer function that returns the next state for a given state and action.
  3. Replace `useState` with `useReducer`.
- Reducers require you to write a bit more code, but they help with debugging and testing.
- Reducers must be pure.
- Each action describes a single user interaction.
- Use Immer if you want to write reducers in a mutating style.




# Passing Data Deeply With Context

Usually, you will pass information from a parent component to a child component via props. But passing props can become verbose and inconvenient if you have to pass them through many components in the middle, or if many components in your app need the same information. *Context* lets the parent component make some information available to any component in the tree below it—no matter how deep—without passing it explicitly through props.

- What "prop drilling" is
- How to replace repetitive prop passing with context
- Common use cases for context
- Common alternatives to context

## The problem with passing props {/*the-problem-with-passing-props*/}

[Passing props](/learn/passing-props-to-a-component) is a great way to explicitly pipe data through your UI tree to the components that use it.

But passing props can become verbose and inconvenient when you need to pass some prop deeply through the tree, or if many components need the same prop. The nearest common ancestor could be far removed from the components that need data, and [lifting state up](/learn/sharing-state-between-components) that high can lead to a situation called "prop drilling".

<DiagramGroup>

<Diagram name="passing_data_lifting_state" height={160} width={608} captionPosition="top" alt="Diagram with a tree of three components. The parent contains a bubble representing a value highlighted in purple. The value flows down to each of the two children, both highlighted in purple." >

Lifting state up

</Diagram>
<Diagram name="passing_data_prop_drilling" height={430} width={608} captionPosition="top" alt="Diagram with a tree of ten nodes, each node with two children or less. The root node contains a bubble representing a value highlighted in purple. The value flows down through the two children, each of which pass the value but do not contain it. The left child passes the value down to two children which are both highlighted purple. The right child of the root passes the value through to one of its two children - the right one, which is highlighted purple. That child passed the value through its single child, which passes it down to both of its two children, which are highlighted purple.">

Prop drilling

</Diagram>

</DiagramGroup>

Wouldn't it be great if there were a way to "teleport" data to the components in the tree that need it without passing props? With React's context feature, there is!

## Context: an alternative to passing props {/*context-an-alternative-to-passing-props*/}

Context lets a parent component provide data to the entire tree below it. There are many uses for context. Here is one example. Consider this `Heading` component that accepts a `level` for its size:

[Interactive example removed — see react.dev for live demo]


Let's say you want multiple headings within the same `Section` to always have the same size:

[Interactive example removed — see react.dev for live demo]


Currently, you pass the `level` prop to each `<Heading>` separately:

```js
<Section>
  <Heading level={3}>About</Heading>
  <Heading level={3}>Photos</Heading>
  <Heading level={3}>Videos</Heading>
</Section>
```

It would be nice if you could pass the `level` prop to the `<Section>` component instead and remove it from the `<Heading>`. This way you could enforce that all headings in the same section have the same size:

```js
<Section level={3}>
  <Heading>About</Heading>
  <Heading>Photos</Heading>
  <Heading>Videos</Heading>
</Section>
```

But how can the `<Heading>` component know the level of its closest `<Section>`? **That would require some way for a child to "ask" for data from somewhere above in the tree.**

You can't do it with props alone. This is where context comes into play. You will do it in three steps:

1. **Create** a context. (You can call it `LevelContext`, since it's for the heading level.)
2. **Use** that context from the component that needs the data. (`Heading` will use `LevelContext`.)
3. **Provide** that context from the component that specifies the data. (`Section` will provide `LevelContext`.)

Context lets a parent--even a distant one!--provide some data to the entire tree inside of it.

<DiagramGroup>

<Diagram name="passing_data_context_close" height={160} width={608} captionPosition="top" alt="Diagram with a tree of three components. The parent contains a bubble representing a value highlighted in orange which projects down to the two children, each highlighted in orange." >

Using context in close children

</Diagram>

<Diagram name="passing_data_context_far" height={430} width={608} captionPosition="top" alt="Diagram with a tree of ten nodes, each node with two children or less. The root parent node contains a bubble representing a value highlighted in orange. The value projects down directly to four leaves and one intermediate component in the tree, which are all highlighted in orange. None of the other intermediate components are highlighted.">

Using context in distant children

</Diagram>

</DiagramGroup>

### Step 1: Create the context {/*step-1-create-the-context*/}

First, you need to create the context. You'll need to **export it from a file** so that your components can use it:

[Interactive example removed — see react.dev for live demo]


The only argument to `createContext` is the _default_ value. Here, `1` refers to the biggest heading level, but you could pass any kind of value (even an object). You will see the significance of the default value in the next step.

### Step 2: Use the context {/*step-2-use-the-context*/}

Import the `useContext` Hook from React and your context:

```js
import { useContext } from 'react';
import { LevelContext } from './LevelContext.js';
```

Currently, the `Heading` component reads `level` from props:

```js
export default function Heading({ level, children }) {
  // ...
}
```

Instead, remove the `level` prop and read the value from the context you just imported, `LevelContext`:

```js {2}
export default function Heading({ children }) {
  const level = useContext(LevelContext);
  // ...
}
```

`useContext` is a Hook. Just like `useState` and `useReducer`, you can only call a Hook immediately inside a React component (not inside loops or conditions). **`useContext` tells React that the `Heading` component wants to read the `LevelContext`.**

Now that the `Heading` component doesn't have a `level` prop, you don't need to pass the level prop to `Heading` in your JSX like this anymore:

```js
<Section>
  <Heading level={4}>Sub-sub-heading</Heading>
  <Heading level={4}>Sub-sub-heading</Heading>
  <Heading level={4}>Sub-sub-heading</Heading>
</Section>
```

Update the JSX so that it's the `Section` that receives it instead:

```jsx
<Section level={4}>
  <Heading>Sub-sub-heading</Heading>
  <Heading>Sub-sub-heading</Heading>
  <Heading>Sub-sub-heading</Heading>
</Section>
```

As a reminder, this is the markup that you were trying to get working:

[Interactive example removed — see react.dev for live demo]


Notice this example doesn't quite work, yet! All the headings have the same size because **even though you're *using* the context, you have not *provided* it yet.** React doesn't know where to get it!

If you don't provide the context, React will use the default value you've specified in the previous step. In this example, you specified `1` as the argument to `createContext`, so `useContext(LevelContext)` returns `1`, setting all those headings to `<h1>`. Let's fix this problem by having each `Section` provide its own context.

### Step 3: Provide the context {/*step-3-provide-the-context*/}

The `Section` component currently renders its children:

```js
export default function Section({ children }) {
  return (
    <section className="section">
      {children}
    </section>
  );
}
```

**Wrap them with a context provider** to provide the `LevelContext` to them:

```js {1,6,8}
import { LevelContext } from './LevelContext.js';

export default function Section({ level, children }) {
  return (
    <section className="section">
      <LevelContext value={level}>
        {children}
      </LevelContext>
    </section>
  );
}
```

This tells React: "if any component inside this `<Section>` asks for `LevelContext`, give them this `level`." The component will use the value of the nearest `<LevelContext>` in the UI tree above it.

[Interactive example removed — see react.dev for live demo]


It's the same result as the original code, but you did not need to pass the `level` prop to each `Heading` component! Instead, it "figures out" its heading level by asking the closest `Section` above:

1. You pass a `level` prop to the `<Section>`.
2. `Section` wraps its children into `<LevelContext value={level}>`.
3. `Heading` asks the closest value of `LevelContext` above with `useContext(LevelContext)`.

## Using and providing context from the same component {/*using-and-providing-context-from-the-same-component*/}

Currently, you still have to specify each section's `level` manually:

```js
export default function Page() {
  return (
    <Section level={1}>
      ...
      <Section level={2}>
        ...
        <Section level={3}>
          ...
```

Since context lets you read information from a component above, each `Section` could read the `level` from the `Section` above, and pass `level + 1` down automatically. Here is how you could do it:

```js src/Section.js {5,8}
import { useContext } from 'react';
import { LevelContext } from './LevelContext.js';

export default function Section({ children }) {
  const level = useContext(LevelContext);
  return (
    <section className="section">
      <LevelContext value={level + 1}>
        {children}
      </LevelContext>
    </section>
  );
}
```

With this change, you don't need to pass the `level` prop *either* to the `<Section>` or to the `<Heading>`:

[Interactive example removed — see react.dev for live demo]


Now both `Heading` and `Section` read the `LevelContext` to figure out how "deep" they are. And the `Section` wraps its children into the `LevelContext` to specify that anything inside of it is at a "deeper" level.

> **Note:**
>
> 
> 
> This example uses heading levels because they show visually how nested components can override context. But context is useful for many other use cases too. You can pass down any information needed by the entire subtree: the current color theme, the currently logged in user, and so on.
> 
> 


## Context passes through intermediate components {/*context-passes-through-intermediate-components*/}

You can insert as many components as you like between the component that provides context and the one that uses it. This includes both built-in components like `<div>` and components you might build yourself.

In this example, the same `Post` component (with a dashed border) is rendered at two different nesting levels. Notice that the `<Heading>` inside of it gets its level automatically from the closest `<Section>`:

[Interactive example removed — see react.dev for live demo]


You didn't do anything special for this to work. A `Section` specifies the context for the tree inside it, so you can insert a `<Heading>` anywhere, and it will have the correct size. Try it in the sandbox above!

**Context lets you write components that "adapt to their surroundings" and display themselves differently depending on _where_ (or, in other words, _in which context_) they are being rendered.**

How context works might remind you of [CSS property inheritance.](https://developer.mozilla.org/en-US/docs/Web/CSS/inheritance) In CSS, you can specify `color: blue` for a `<div>`, and any DOM node inside of it, no matter how deep, will inherit that color unless some other DOM node in the middle overrides it with `color: green`. Similarly, in React, the only way to override some context coming from above is to wrap children into a context provider with a different value.

In CSS, different properties like `color` and `background-color` don't override each other. You can set all  `<div>`'s `color` to red without impacting `background-color`. Similarly, **different React contexts don't override each other.** Each context that you make with `createContext()` is completely separate from other ones, and ties together components using and providing *that particular* context. One component may use or provide many different contexts without a problem.

## Before you use context {/*before-you-use-context*/}

Context is very tempting to use! However, this also means it's too easy to overuse it. **Just because you need to pass some props several levels deep doesn't mean you should put that information into context.**

Here's a few alternatives you should consider before using context:

1. **Start by [passing props.](/learn/passing-props-to-a-component)** If your components are not trivial, it's not unusual to pass a dozen props down through a dozen components. It may feel like a slog, but it makes it very clear which components use which data! The person maintaining your code will be glad you've made the data flow explicit with props.
2. **Extract components and [pass JSX as `children`](/learn/passing-props-to-a-component#passing-jsx-as-children) to them.** If you pass some data through many layers of intermediate components that don't use that data (and only pass it further down), this often means that you forgot to extract some components along the way. For example, maybe you pass data props like `posts` to visual components that don't use them directly, like `<Layout posts={posts} />`. Instead, make `Layout` take `children` as a prop, and render `<Layout><Posts posts={posts} /></Layout>`. This reduces the number of layers between the component specifying the data and the one that needs it.

If neither of these approaches works well for you, consider context.

## Use cases for context {/*use-cases-for-context*/}

* **Theming:** If your app lets the user change its appearance (e.g. dark mode), you can put a context provider at the top of your app, and use that context in components that need to adjust their visual look.
* **Current account:** Many components might need to know the currently logged in user. Putting it in context makes it convenient to read it anywhere in the tree. Some apps also let you operate multiple accounts at the same time (e.g. to leave a comment as a different user). In those cases, it can be convenient to wrap a part of the UI into a nested provider with a different current account value.
* **Routing:** Most routing solutions use context internally to hold the current route. This is how every link "knows" whether it's active or not. If you build your own router, you might want to do it too.
* **Managing state:** As your app grows, you might end up with a lot of state closer to the top of your app. Many distant components below may want to change it. It is common to [use a reducer together with context](/learn/scaling-up-with-reducer-and-context) to manage complex state and pass it down to distant components without too much hassle.
  
Context is not limited to static values. If you pass a different value on the next render, React will update all the components reading it below! This is why context is often used in combination with state.

In general, if some information is needed by distant components in different parts of the tree, it's a good indication that context will help you.

* Context lets a component provide some information to the entire tree below it.
* To pass context:
  1. Create and export it with `export const MyContext = createContext(defaultValue)`.
  2. Pass it to the `useContext(MyContext)` Hook to read it in any child component, no matter how deep.
  3. Wrap children into `<MyContext value={...}>` to provide it from a parent.
* Context passes through any components in the middle.
* Context lets you write components that "adapt to their surroundings".
* Before you use context, try passing props or passing JSX as `children`.




# Scaling Up With Reducer And Context

Reducers let you consolidate a component's state update logic. Context lets you pass information deep down to other components. You can combine reducers and context together to manage state of a complex screen.

* How to combine a reducer with context
* How to avoid passing state and dispatch through props
* How to keep context and state logic in a separate file

## Combining a reducer with context {/*combining-a-reducer-with-context*/}

In this example from [the introduction to reducers](/learn/extracting-state-logic-into-a-reducer), the state is managed by a reducer. The reducer function contains all of the state update logic and is declared at the bottom of this file:

[Interactive example removed — see react.dev for live demo]


A reducer helps keep the event handlers short and concise. However, as your app grows, you might run into another difficulty. **Currently, the `tasks` state and the `dispatch` function are only available in the top-level `TaskApp` component.** To let other components read the list of tasks or change it, you have to explicitly [pass down](/learn/passing-props-to-a-component) the current state and the event handlers that change it as props.

For example, `TaskApp` passes a list of tasks and the event handlers to `TaskList`:

```js
<TaskList
  tasks={tasks}
  onChangeTask={handleChangeTask}
  onDeleteTask={handleDeleteTask}
/>
```

And `TaskList` passes the event handlers to `Task`:

```js
<Task
  task={task}
  onChange={onChangeTask}
  onDelete={onDeleteTask}
/>
```

In a small example like this, this works well, but if you have tens or hundreds of components in the middle, passing down all state and functions can be quite frustrating!

This is why, as an alternative to passing them through props, you might want to put both the `tasks` state and the `dispatch` function [into context.](/learn/passing-data-deeply-with-context) **This way, any component below `TaskApp` in the tree can read the tasks and dispatch actions without the repetitive "prop drilling".**

Here is how you can combine a reducer with context:

1. **Create** the context.
2. **Put** state and dispatch into context.
3. **Use** context anywhere in the tree.

### Step 1: Create the context {/*step-1-create-the-context*/}

The `useReducer` Hook returns the current `tasks` and the `dispatch` function that lets you update them:

```js
const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
```

To pass them down the tree, you will [create](/learn/passing-data-deeply-with-context#step-2-use-the-context) two separate contexts:

- `TasksContext` provides the current list of tasks.
- `TasksDispatchContext` provides the function that lets components dispatch actions.

Export them from a separate file so that you can later import them from other files:

[Interactive example removed — see react.dev for live demo]


Here, you're passing `null` as the default value to both contexts. The actual values will be provided by the `TaskApp` component.

### Step 2: Put state and dispatch into context {/*step-2-put-state-and-dispatch-into-context*/}

Now you can import both contexts in your `TaskApp` component. Take the `tasks` and `dispatch` returned by `useReducer()` and [provide them](/learn/passing-data-deeply-with-context#step-3-provide-the-context) to the entire tree below:

```js {4,7-8}
import { TasksContext, TasksDispatchContext } from './TasksContext.js';

export default function TaskApp() {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);
  // ...
  return (
    <TasksContext value={tasks}>
      <TasksDispatchContext value={dispatch}>
        ...
      </TasksDispatchContext>
    </TasksContext>
  );
}
```

For now, you pass the information both via props and in context:

[Interactive example removed — see react.dev for live demo]


In the next step, you will remove prop passing.

### Step 3: Use context anywhere in the tree {/*step-3-use-context-anywhere-in-the-tree*/}

Now you don't need to pass the list of tasks or the event handlers down the tree:

```js {4-5}
<TasksContext value={tasks}>
  <TasksDispatchContext value={dispatch}>
    <h1>Day off in Kyoto</h1>
    <AddTask />
    <TaskList />
  </TasksDispatchContext>
</TasksContext>
```

Instead, any component that needs the task list can read it from the `TasksContext`:

```js {2}
export default function TaskList() {
  const tasks = useContext(TasksContext);
  // ...
```

To update the task list, any component can read the `dispatch` function from context and call it:

```js {3,9-13}
export default function AddTask() {
  const [text, setText] = useState('');
  const dispatch = useContext(TasksDispatchContext);
  // ...
  return (
    // ...
    <button onClick={() => {
      setText('');
      dispatch({
        type: 'added',
        id: nextId++,
        text: text,
      });
    }}>Add</button>
    // ...
```

**The `TaskApp` component does not pass any event handlers down, and the `TaskList` does not pass any event handlers to the `Task` component either.** Each component reads the context that it needs:

[Interactive example removed — see react.dev for live demo]


**The state still "lives" in the top-level `TaskApp` component, managed with `useReducer`.** But its `tasks` and `dispatch` are now available to every component below in the tree by importing and using these contexts.

## Moving all wiring into a single file {/*moving-all-wiring-into-a-single-file*/}

You don't have to do this, but you could further declutter the components by moving both reducer and context into a single file. Currently, `TasksContext.js` contains only two context declarations:

```js
import { createContext } from 'react';

export const TasksContext = createContext(null);
export const TasksDispatchContext = createContext(null);
```

This file is about to get crowded! You'll move the reducer into that same file. Then you'll declare a new `TasksProvider` component in the same file. This component will tie all the pieces together:

1. It will manage the state with a reducer.
2. It will provide both contexts to components below.
3. It will [take `children` as a prop](/learn/passing-props-to-a-component#passing-jsx-as-children) so you can pass JSX to it.

```js
export function TasksProvider({ children }) {
  const [tasks, dispatch] = useReducer(tasksReducer, initialTasks);

  return (
    <TasksContext value={tasks}>
      <TasksDispatchContext value={dispatch}>
        {children}
      </TasksDispatchContext>
    </TasksContext>
  );
}
```

**This removes all the complexity and wiring from your `TaskApp` component:**

[Interactive example removed — see react.dev for live demo]


You can also export functions that _use_ the context from `TasksContext.js`:

```js
export function useTasks() {
  return useContext(TasksContext);
}

export function useTasksDispatch() {
  return useContext(TasksDispatchContext);
}
```

When a component needs to read context, it can do it through these functions:

```js
const tasks = useTasks();
const dispatch = useTasksDispatch();
```

This doesn't change the behavior in any way, but it lets you later split these contexts further or add some logic to these functions. **Now all of the context and reducer wiring is in `TasksContext.js`. This keeps the components clean and uncluttered, focused on what they display rather than where they get the data:**

[Interactive example removed — see react.dev for live demo]


You can think of `TasksProvider` as a part of the screen that knows how to deal with tasks, `useTasks` as a way to read them, and `useTasksDispatch` as a way to update them from any component below in the tree.

> **Note:**
>
> 
> 
> Functions like `useTasks` and `useTasksDispatch` are called *[Custom Hooks.](/learn/reusing-logic-with-custom-hooks)* Your function is considered a custom Hook if its name starts with `use`. This lets you use other Hooks, like `useContext`, inside it.
> 
> 


As your app grows, you may have many context-reducer pairs like this. This is a powerful way to scale your app and [lift state up](/learn/sharing-state-between-components) without too much work whenever you want to access the data deep in the tree.

- You can combine reducer with context to let any component read and update state above it.
- To provide state and the dispatch function to components below:
  1. Create two contexts (for state and for dispatch functions).
  2. Provide both contexts from the component that uses the reducer.
  3. Use either context from components that need to read them.
- You can further declutter the components by moving all wiring into one file.
  - You can export a component like `TasksProvider` that provides context.
  - You can also export custom Hooks like `useTasks` and `useTasksDispatch` to read it.
- You can have many context-reducer pairs like this in your app.


# Usereducer

`useReducer` is a React Hook that lets you add a [reducer](/learn/extracting-state-logic-into-a-reducer) to your component.

```js
const [state, dispatch] = useReducer(reducer, initialArg, init?)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useReducer(reducer, initialArg, init?)` {/*usereducer*/}

Call `useReducer` at the top level of your component to manage its state with a [reducer.](/learn/extracting-state-logic-into-a-reducer)

```js
import { useReducer } from 'react';

function reducer(state, action) {
  // ...
}

function MyComponent() {
  const [state, dispatch] = useReducer(reducer, { age: 42 });
  // ...
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `reducer`: The reducer function that specifies how the state gets updated. It must be pure, should take the state and action as arguments, and should return the next state. State and action can be of any types. 
* `initialArg`: The value from which the initial state is calculated. It can be a value of any type. How the initial state is calculated from it depends on the next `init` argument.
* **optional** `init`: The initializer function that should return the initial state. If it's not specified, the initial state is set to `initialArg`. Otherwise, the initial state is set to the result of calling `init(initialArg)`.

#### Returns {/*returns*/}

`useReducer` returns an array with exactly two values:

1. The current state. During the first render, it's set to `init(initialArg)` or `initialArg` (if there's no `init`).
2. The [`dispatch` function](#dispatch) that lets you update the state to a different value and trigger a re-render.

#### Caveats {/*caveats*/}

* `useReducer` is a Hook, so you can only call it **at the top level of your component** or your own Hooks. You can't call it inside loops or conditions. If you need that, extract a new component and move the state into it.
* The `dispatch` function has a stable identity, so you will often see it omitted from Effect dependencies, but including it will not cause the Effect to fire. If the linter lets you omit a dependency without errors, it is safe to do. [Learn more about removing Effect dependencies.](/learn/removing-effect-dependencies#move-dynamic-objects-and-functions-inside-your-effect)
* In Strict Mode, React will **call your reducer and initializer twice** in order to [help you find accidental impurities.](#my-reducer-or-initializer-function-runs-twice) This is development-only behavior and does not affect production. If your reducer and initializer are pure (as they should be), this should not affect your logic. The result from one of the calls is ignored.

---

### `dispatch` function {/*dispatch*/}

The `dispatch` function returned by `useReducer` lets you update the state to a different value and trigger a re-render. You need to pass the action as the only argument to the `dispatch` function:

```js
const [state, dispatch] = useReducer(reducer, { age: 42 });

function handleClick() {
  dispatch({ type: 'incremented_age' });
  // ...
```

React will set the next state to the result of calling the `reducer` function you've provided with the current `state` and the action you've passed to `dispatch`.

#### Parameters {/*dispatch-parameters*/}

* `action`: The action performed by the user. It can be a value of any type. By convention, an action is usually an object with a `type` property identifying it and, optionally, other properties with additional information.

#### Returns {/*dispatch-returns*/}

`dispatch` functions do not have a return value.

#### Caveats {/*setstate-caveats*/}

* The `dispatch` function **only updates the state variable for the *next* render**. If you read the state variable after calling the `dispatch` function, [you will still get the old value](#ive-dispatched-an-action-but-logging-gives-me-the-old-state-value) that was on the screen before your call.

* If the new value you provide is identical to the current `state`, as determined by an [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison, React will **skip re-rendering the component and its children.** This is an optimization. React may still need to call your component before ignoring the result, but it shouldn't affect your code.

* React [batches state updates.](/learn/queueing-a-series-of-state-updates) It updates the screen **after all the event handlers have run** and have called their `set` functions. This prevents multiple re-renders during a single event. In the rare case that you need to force React to update the screen earlier, for example to access the DOM, you can use [`flushSync`.](/reference/react-dom/flushSync)

---

## Usage {/*usage*/}

### Adding a reducer to a component {/*adding-a-reducer-to-a-component*/}

Call `useReducer` at the top level of your component to manage state with a [reducer.](/learn/extracting-state-logic-into-a-reducer)

```js [[1, 8, "state"], [2, 8, "dispatch"], [4, 8, "reducer"], [3, 8, "{ age: 42 }"]]
import { useReducer } from 'react';

function reducer(state, action) {
  // ...
}

function MyComponent() {
  const [state, dispatch] = useReducer(reducer, { age: 42 });
  // ...
```

`useReducer` returns an array with exactly two items:

1. The current state of this state variable, initially set to the initial state you provided.
2. The `dispatch` function that lets you change it in response to interaction.

To update what's on the screen, call `dispatch` with an object representing what the user did, called an *action*:

```js [[2, 2, "dispatch"]]
function handleClick() {
  dispatch({ type: 'incremented_age' });
}
```

React will pass the current state and the action to your reducer function. Your reducer will calculate and return the next state. React will store that next state, render your component with it, and update the UI.

[Interactive example removed — see react.dev for live demo]


`useReducer` is very similar to [`useState`](/reference/react/useState), but it lets you move the state update logic from event handlers into a single function outside of your component. Read more about [choosing between `useState` and `useReducer`.](/learn/extracting-state-logic-into-a-reducer#comparing-usestate-and-usereducer)

---

### Writing the reducer function {/*writing-the-reducer-function*/}

A reducer function is declared like this:

```js
function reducer(state, action) {
  // ...
}
```

Then you need to fill in the code that will calculate and return the next state. By convention, it is common to write it as a [`switch` statement.](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/switch) For each `case` in the `switch`, calculate and return some next state.

```js {4-7,10-13}
function reducer(state, action) {
  switch (action.type) {
    case 'incremented_age': {
      return {
        name: state.name,
        age: state.age + 1
      };
    }
    case 'changed_name': {
      return {
        name: action.nextName,
        age: state.age
      };
    }
  }
  throw Error('Unknown action: ' + action.type);
}
```

Actions can have any shape. By convention, it's common to pass objects with a `type` property identifying the action. It should include the minimal necessary information that the reducer needs to compute the next state.

```js {5,9-12}
function Form() {
  const [state, dispatch] = useReducer(reducer, { name: 'Taylor', age: 42 });
  
  function handleButtonClick() {
    dispatch({ type: 'incremented_age' });
  }

  function handleInputChange(e) {
    dispatch({
      type: 'changed_name',
      nextName: e.target.value
    });
  }
  // ...
```

The action type names are local to your component. [Each action describes a single interaction, even if that leads to multiple changes in data.](/learn/extracting-state-logic-into-a-reducer#writing-reducers-well) The shape of the state is arbitrary, but usually it'll be an object or an array.

Read [extracting state logic into a reducer](/learn/extracting-state-logic-into-a-reducer) to learn more.

> **Pitfall:**
>
> 
> 
> State is read-only. Don't modify any objects or arrays in state:
> 
> ```js {4,5}
> function reducer(state, action) {
>   switch (action.type) {
>     case 'incremented_age': {
>       // 🚩 Don't mutate an object in state like this:
>       state.age = state.age + 1;
>       return state;
>     }
> ```
> 
> Instead, always return new objects from your reducer:
> 
> ```js {4-8}
> function reducer(state, action) {
>   switch (action.type) {
>     case 'incremented_age': {
>       // ✅ Instead, return a new object
>       return {
>         ...state,
>         age: state.age + 1
>       };
>     }
> ```
> 
> Read [updating objects in state](/learn/updating-objects-in-state) and [updating arrays in state](/learn/updating-arrays-in-state) to learn more.
> 
> 


<Recipes titleText="Basic useReducer examples" titleId="examples-basic">

#### Form (object) {/*form-object*/}

In this example, the reducer manages a state object with two fields: `name` and `age`.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Todo list (array) {/*todo-list-array*/}

In this example, the reducer manages an array of tasks. The array needs to be updated [without mutation.](/learn/updating-arrays-in-state)

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Writing concise update logic with Immer {/*writing-concise-update-logic-with-immer*/}

If updating arrays and objects without mutation feels tedious, you can use a library like [Immer](https://github.com/immerjs/use-immer#useimmerreducer) to reduce repetitive code. Immer lets you write concise code as if you were mutating objects, but under the hood it performs immutable updates:

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Avoiding recreating the initial state {/*avoiding-recreating-the-initial-state*/}

React saves the initial state once and ignores it on the next renders.

```js
function createInitialState(username) {
  // ...
}

function TodoList({ username }) {
  const [state, dispatch] = useReducer(reducer, createInitialState(username));
  // ...
```

Although the result of `createInitialState(username)` is only used for the initial render, you're still calling this function on every render. This can be wasteful if it's creating large arrays or performing expensive calculations.

To solve this, you may **pass it as an _initializer_ function** to `useReducer` as the third argument instead:

```js {6}
function createInitialState(username) {
  // ...
}

function TodoList({ username }) {
  const [state, dispatch] = useReducer(reducer, username, createInitialState);
  // ...
```

Notice that you’re passing `createInitialState`, which is the *function itself*, and not `createInitialState()`, which is the result of calling it. This way, the initial state does not get re-created after initialization.

In the above example, `createInitialState` takes a `username` argument. If your initializer doesn't need any information to compute the initial state, you may pass `null` as the second argument to `useReducer`.

<Recipes titleText="The difference between passing an initializer and passing the initial state directly" titleId="examples-initializer">

#### Passing the initializer function {/*passing-the-initializer-function*/}

This example passes the initializer function, so the `createInitialState` function only runs during initialization. It does not run when component re-renders, such as when you type into the input.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Passing the initial state directly {/*passing-the-initial-state-directly*/}

This example **does not** pass the initializer function, so the `createInitialState` function runs on every render, such as when you type into the input. There is no observable difference in behavior, but this code is less efficient.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

## Troubleshooting {/*troubleshooting*/}

### I've dispatched an action, but logging gives me the old state value {/*ive-dispatched-an-action-but-logging-gives-me-the-old-state-value*/}

Calling the `dispatch` function **does not change state in the running code**:

```js {4,5,8}
function handleClick() {
  console.log(state.age);  // 42

  dispatch({ type: 'incremented_age' }); // Request a re-render with 43
  console.log(state.age);  // Still 42!

  setTimeout(() => {
    console.log(state.age); // Also 42!
  }, 5000);
}
```

This is because [states behaves like a snapshot.](/learn/state-as-a-snapshot) Updating state requests another render with the new state value, but does not affect the `state` JavaScript variable in your already-running event handler.

If you need to guess the next state value, you can calculate it manually by calling the reducer yourself:

```js
const action = { type: 'incremented_age' };
dispatch(action);

const nextState = reducer(state, action);
console.log(state);     // { age: 42 }
console.log(nextState); // { age: 43 }
```

---

### I've dispatched an action, but the screen doesn't update {/*ive-dispatched-an-action-but-the-screen-doesnt-update*/}

React will **ignore your update if the next state is equal to the previous state,** as determined by an [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison. This usually happens when you change an object or an array in state directly:

```js {4-5,9-10}
function reducer(state, action) {
  switch (action.type) {
    case 'incremented_age': {
      // 🚩 Wrong: mutating existing object
      state.age++;
      return state;
    }
    case 'changed_name': {
      // 🚩 Wrong: mutating existing object
      state.name = action.nextName;
      return state;
    }
    // ...
  }
}
```

You mutated an existing `state` object and returned it, so React ignored the update. To fix this, you need to ensure that you're always [updating objects in state](/learn/updating-objects-in-state) and [updating arrays in state](/learn/updating-arrays-in-state) instead of mutating them:

```js {4-8,11-15}
function reducer(state, action) {
  switch (action.type) {
    case 'incremented_age': {
      // ✅ Correct: creating a new object
      return {
        ...state,
        age: state.age + 1
      };
    }
    case 'changed_name': {
      // ✅ Correct: creating a new object
      return {
        ...state,
        name: action.nextName
      };
    }
    // ...
  }
}
```

---

### A part of my reducer state becomes undefined after dispatching {/*a-part-of-my-reducer-state-becomes-undefined-after-dispatching*/}

Make sure that every `case` branch **copies all of the existing fields** when returning the new state:

```js {5}
function reducer(state, action) {
  switch (action.type) {
    case 'incremented_age': {
      return {
        ...state, // Don't forget this!
        age: state.age + 1
      };
    }
    // ...
```

Without `...state` above, the returned next state would only contain the `age` field and nothing else.

---

### My entire reducer state becomes undefined after dispatching {/*my-entire-reducer-state-becomes-undefined-after-dispatching*/}

If your state unexpectedly becomes `undefined`, you're likely forgetting to `return` state in one of the cases, or your action type doesn't match any of the `case` statements. To find why, throw an error outside the `switch`:

```js {10}
function reducer(state, action) {
  switch (action.type) {
    case 'incremented_age': {
      // ...
    }
    case 'edited_name': {
      // ...
    }
  }
  throw Error('Unknown action: ' + action.type);
}
```

You can also use a static type checker like TypeScript to catch such mistakes.

---

### I'm getting an error: "Too many re-renders" {/*im-getting-an-error-too-many-re-renders*/}

You might get an error that says: `Too many re-renders. React limits the number of renders to prevent an infinite loop.` Typically, this means that you're unconditionally dispatching an action *during render*, so your component enters a loop: render, dispatch (which causes a render), render, dispatch (which causes a render), and so on. Very often, this is caused by a mistake in specifying an event handler:

```js {1-2}
// 🚩 Wrong: calls the handler during render
return <button onClick={handleClick()}>Click me</button>

// ✅ Correct: passes down the event handler
return <button onClick={handleClick}>Click me</button>

// ✅ Correct: passes down an inline function
return <button onClick={(e) => handleClick(e)}>Click me</button>
```

If you can't find the cause of this error, click on the arrow next to the error in the console and look through the JavaScript stack to find the specific `dispatch` function call responsible for the error.

---

### My reducer or initializer function runs twice {/*my-reducer-or-initializer-function-runs-twice*/}

In [Strict Mode](/reference/react/StrictMode), React will call your reducer and initializer functions twice. This shouldn't break your code.

This **development-only** behavior helps you [keep components pure.](/learn/keeping-components-pure) React uses the result of one of the calls, and ignores the result of the other call. As long as your component, initializer, and reducer functions are pure, this shouldn't affect your logic. However, if they are accidentally impure, this helps you notice the mistakes.

For example, this impure reducer function mutates an array in state:

```js {4-6}
function reducer(state, action) {
  switch (action.type) {
    case 'added_todo': {
      // 🚩 Mistake: mutating state
      state.todos.push({ id: nextId++, text: action.text });
      return state;
    }
    // ...
  }
}
```

Because React calls your reducer function twice, you'll see the todo was added twice, so you'll know that there is a mistake. In this example, you can fix the mistake by [replacing the array instead of mutating it](/learn/updating-arrays-in-state#adding-to-an-array):

```js {4-11}
function reducer(state, action) {
  switch (action.type) {
    case 'added_todo': {
      // ✅ Correct: replacing with new state
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: nextId++, text: action.text }
        ]
      };
    }
    // ...
  }
}
```

Now that this reducer function is pure, calling it an extra time doesn't make a difference in behavior. This is why React calling it twice helps you find mistakes. **Only component, initializer, and reducer functions need to be pure.** Event handlers don't need to be pure, so React will never call your event handlers twice.

Read [keeping components pure](/learn/keeping-components-pure) to learn more.


# Usecontext

`useContext` is a React Hook that lets you read and subscribe to [context](/learn/passing-data-deeply-with-context) from your component.

```js
const value = useContext(SomeContext)
```

<InlineToc />

---

## Reference {/*reference*/}

### `useContext(SomeContext)` {/*usecontext*/}

Call `useContext` at the top level of your component to read and subscribe to [context.](/learn/passing-data-deeply-with-context)

```js
import { useContext } from 'react';

function MyComponent() {
  const theme = useContext(ThemeContext);
  // ...
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `SomeContext`: The context that you've previously created with [`createContext`](/reference/react/createContext). The context itself does not hold the information, it only represents the kind of information you can provide or read from components.

#### Returns {/*returns*/}

`useContext` returns the context value for the calling component. It is determined as the `value` passed to the closest `SomeContext` above the calling component in the tree. If there is no such provider, then the returned value will be the `defaultValue` you have passed to [`createContext`](/reference/react/createContext) for that context. The returned value is always up-to-date. React automatically re-renders components that read some context if it changes.

#### Caveats {/*caveats*/}

* `useContext()` call in a component is not affected by providers returned from the *same* component. The corresponding `<Context>` **needs to be *above*** the component doing the `useContext()` call.
* React **automatically re-renders** all the children that use a particular context starting from the provider that receives a different `value`. The previous and the next values are compared with the [`Object.is`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/is) comparison. Skipping re-renders with [`memo`](/reference/react/memo) does not prevent the children receiving fresh context values.
* If your build system produces duplicates modules in the output (which can happen with symlinks), this can break context. Passing something via context only works if `SomeContext` that you use to provide context and `SomeContext` that you use to read it are ***exactly* the same object**, as determined by a `===` comparison.

---

## Usage {/*usage*/}


### Passing data deeply into the tree {/*passing-data-deeply-into-the-tree*/}

Call `useContext` at the top level of your component to read and subscribe to [context.](/learn/passing-data-deeply-with-context)

```js [[2, 4, "theme"], [1, 4, "ThemeContext"]]
import { useContext } from 'react';

function Button() {
  const theme = useContext(ThemeContext);
  // ... 
```

`useContext` returns the context value for the context you passed. To determine the context value, React searches the component tree and finds **the closest context provider above** for that particular context.

To pass context to a `Button`, wrap it or one of its parent components into the corresponding context provider:

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

It doesn't matter how many layers of components there are between the provider and the `Button`. When a `Button` *anywhere* inside of `Form` calls `useContext(ThemeContext)`, it will receive `"dark"` as the value.

> **Pitfall:**
>
> 
> 
> `useContext()` always looks for the closest provider *above* the component that calls it. It searches upwards and **does not** consider providers in the component from which you're calling `useContext()`.
> 
> 


[Interactive example removed — see react.dev for live demo]


---

### Updating data passed via context {/*updating-data-passed-via-context*/}

Often, you'll want the context to change over time. To update context, combine it with [state.](/reference/react/useState) Declare a state variable in the parent component, and pass the current state down as the context value to the provider.

```js {2} [[1, 4, "ThemeContext"], [2, 4, "theme"], [1, 11, "ThemeContext"]]
function MyPage() {
  const [theme, setTheme] = useState('dark');
  return (
    <ThemeContext value={theme}>
      <Form />
      <Button onClick={() => {
        setTheme('light');
      }}>
        Switch to light theme
      </Button>
    </ThemeContext>
  );
}
```

Now any `Button` inside of the provider will receive the current `theme` value. If you call `setTheme` to update the `theme` value that you pass to the provider, all `Button` components will re-render with the new `'light'` value.

<Recipes titleText="Examples of updating context" titleId="examples-basic">

#### Updating a value via context {/*updating-a-value-via-context*/}

In this example, the `MyApp` component holds a state variable which is then passed to the `ThemeContext` provider. Checking the "Dark mode" checkbox updates the state. Changing the provided value re-renders all the components using that context.

[Interactive example removed — see react.dev for live demo]


Note that `value="dark"` passes the `"dark"` string, but `value={theme}` passes the value of the JavaScript `theme` variable with [JSX curly braces.](/learn/javascript-in-jsx-with-curly-braces) Curly braces also let you pass context values that aren't strings.

<Solution />

#### Updating an object via context {/*updating-an-object-via-context*/}

In this example, there is a `currentUser` state variable which holds an object. You combine `{ currentUser, setCurrentUser }` into a single object and pass it down through the context inside the `value={}`. This lets any component below, such as `LoginButton`, read both `currentUser` and `setCurrentUser`, and then call `setCurrentUser` when needed.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Multiple contexts {/*multiple-contexts*/}

In this example, there are two independent contexts. `ThemeContext` provides the current theme, which is a string, while `CurrentUserContext` holds the object representing the current user.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Extracting providers to a component {/*extracting-providers-to-a-component*/}

As your app grows, it is expected that you'll have a "pyramid" of contexts closer to the root of your app. There is nothing wrong with that. However, if you dislike the nesting aesthetically, you can extract the providers into a single component. In this example, `MyProviders` hides the "plumbing" and renders the children passed to it inside the necessary providers. Note that the `theme` and `setTheme` state is needed in `MyApp` itself, so `MyApp` still owns that piece of the state.

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Scaling up with context and a reducer {/*scaling-up-with-context-and-a-reducer*/}

In larger apps, it is common to combine context with a [reducer](/reference/react/useReducer) to extract the logic related to some state out of components. In this example, all the "wiring" is hidden in the `TasksContext.js`, which contains a reducer and two separate contexts.

Read a [full walkthrough](/learn/scaling-up-with-reducer-and-context) of this example.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Specifying a fallback default value {/*specifying-a-fallback-default-value*/}

If React can't find any providers of that particular context in the parent tree, the context value returned by `useContext()` will be equal to the default value that you specified when you [created that context](/reference/react/createContext):

```js [[1, 1, "ThemeContext"], [3, 1, "null"]]
const ThemeContext = createContext(null);
```

The default value **never changes**. If you want to update context, use it with state as [described above.](#updating-data-passed-via-context)

Often, instead of `null`, there is some more meaningful value you can use as a default, for example:

```js [[1, 1, "ThemeContext"], [3, 1, "light"]]
const ThemeContext = createContext('light');
```

This way, if you accidentally render some component without a corresponding provider, it won't break. This also helps your components work well in a test environment without setting up a lot of providers in the tests.

In the example below, the "Toggle theme" button is always light because it's **outside any theme context provider** and the default context theme value is `'light'`. Try editing the default theme to be `'dark'`.

[Interactive example removed — see react.dev for live demo]


---

### Overriding context for a part of the tree {/*overriding-context-for-a-part-of-the-tree*/}

You can override the context for a part of the tree by wrapping that part in a provider with a different value.

```js {3,5}
<ThemeContext value="dark">
  ...
  <ThemeContext value="light">
    <Footer />
  </ThemeContext>
  ...
</ThemeContext>
```

You can nest and override providers as many times as you need.

<Recipes titleText="Examples of overriding context">

#### Overriding a theme {/*overriding-a-theme*/}

Here, the button *inside* the `Footer` receives a different context value (`"light"`) than the buttons outside (`"dark"`).

[Interactive example removed — see react.dev for live demo]


<Solution />

#### Automatically nested headings {/*automatically-nested-headings*/}

You can "accumulate" information when you nest context providers. In this example, the `Section` component keeps track of the `LevelContext` which specifies the depth of the section nesting. It reads the `LevelContext` from the parent section, and provides the `LevelContext` number increased by one to its children. As a result, the `Heading` component can automatically decide which of the `<h1>`, `<h2>`, `<h3>`, ..., tags to use based on how many `Section` components it is nested inside of.

Read a [detailed walkthrough](/learn/passing-data-deeply-with-context) of this example.

[Interactive example removed — see react.dev for live demo]


<Solution />

</Recipes>

---

### Optimizing re-renders when passing objects and functions {/*optimizing-re-renders-when-passing-objects-and-functions*/}

You can pass any values via context, including objects and functions.

```js [[2, 10, "{ currentUser, login }"]] 
function MyApp() {
  const [currentUser, setCurrentUser] = useState(null);

  function login(response) {
    storeCredentials(response.credentials);
    setCurrentUser(response.user);
  }

  return (
    <AuthContext value={{ currentUser, login }}>
      <Page />
    </AuthContext>
  );
}
```

Here, the context value is a JavaScript object with two properties, one of which is a function. Whenever `MyApp` re-renders (for example, on a route update), this will be a *different* object pointing at a *different* function, so React will also have to re-render all components deep in the tree that call `useContext(AuthContext)`.

In smaller apps, this is not a problem. However, there is no need to re-render them if the underlying data, like `currentUser`, has not changed. To help React take advantage of that fact, you may wrap the `login` function with [`useCallback`](/reference/react/useCallback) and wrap the object creation into [`useMemo`](/reference/react/useMemo). This is a performance optimization:

```js {6,9,11,14,17}
import { useCallback, useMemo } from 'react';

function MyApp() {
  const [currentUser, setCurrentUser] = useState(null);

  const login = useCallback((response) => {
    storeCredentials(response.credentials);
    setCurrentUser(response.user);
  }, []);

  const contextValue = useMemo(() => ({
    currentUser,
    login
  }), [currentUser, login]);

  return (
    <AuthContext value={contextValue}>
      <Page />
    </AuthContext>
  );
}
```

As a result of this change, even if `MyApp` needs to re-render, the components calling `useContext(AuthContext)` won't need to re-render unless `currentUser` has changed.

Read more about [`useMemo`](/reference/react/useMemo#skipping-re-rendering-of-components) and [`useCallback`.](/reference/react/useCallback#skipping-re-rendering-of-components)

---

## Troubleshooting {/*troubleshooting*/}

### My component doesn't see the value from my provider {/*my-component-doesnt-see-the-value-from-my-provider*/}

There are a few common ways that this can happen:

1. You're rendering `<SomeContext>` in the same component (or below) as where you're calling `useContext()`. Move `<SomeContext>` *above and outside* the component calling `useContext()`.
2. You may have forgotten to wrap your component with `<SomeContext>`, or you might have put it in a different part of the tree than you thought. Check whether the hierarchy is right using [React DevTools.](/learn/react-developer-tools)
3. You might be running into some build issue with your tooling that causes `SomeContext` as seen from the providing component and `SomeContext` as seen by the reading component to be two different objects. This can happen if you use symlinks, for example. You can verify this by assigning them to globals like `window.SomeContext1` and `window.SomeContext2` and then checking whether `window.SomeContext1 === window.SomeContext2` in the console. If they're not the same, fix that issue on the build tool level.

### I am always getting `undefined` from my context although the default value is different {/*i-am-always-getting-undefined-from-my-context-although-the-default-value-is-different*/}

You might have a provider without a `value` in the tree:

```js {1,2}
// 🚩 Doesn't work: no value prop
<ThemeContext>
   <Button />
</ThemeContext>
```

If you forget to specify `value`, it's like passing `value={undefined}`.

You may have also mistakingly used a different prop name by mistake:

```js {1,2}
// 🚩 Doesn't work: prop should be called "value"
<ThemeContext theme={theme}>
   <Button />
</ThemeContext>
```

In both of these cases you should see a warning from React in the console. To fix them, call the prop `value`:

```js {1,2}
// ✅ Passing the value prop
<ThemeContext value={theme}>
   <Button />
</ThemeContext>
```

Note that the [default value from your `createContext(defaultValue)` call](#specifying-a-fallback-default-value) is only used **if there is no matching provider above at all.** If there is a `<SomeContext value={undefined}>` component somewhere in the parent tree, the component calling `useContext(SomeContext)` *will* receive `undefined` as the context value.


# Createcontext

`createContext` lets you create a [context](/learn/passing-data-deeply-with-context) that components can provide or read.

```js
const SomeContext = createContext(defaultValue)
```

<InlineToc />

---

## Reference {/*reference*/}

### `createContext(defaultValue)` {/*createcontext*/}

Call `createContext` outside of any components to create a context.

```js
import { createContext } from 'react';

const ThemeContext = createContext('light');
```

[See more examples below.](#usage)

#### Parameters {/*parameters*/}

* `defaultValue`: The value that you want the context to have when there is no matching context provider in the tree above the component that reads context. If you don't have any meaningful default value, specify `null`. The default value is meant as a "last resort" fallback. It is static and never changes over time.

#### Returns {/*returns*/}

`createContext` returns a context object.

**The context object itself does not hold any information.** It represents _which_ context other components read or provide. Typically, you will use [`SomeContext`](#provider) in components above to specify the context value, and call [`useContext(SomeContext)`](/reference/react/useContext) in components below to read it. The context object has a few properties:

* `SomeContext` lets you provide the context value to components.
* `SomeContext.Consumer` is an alternative and rarely used way to read the context value.
* `SomeContext.Provider` is a legacy way to provide the context value before React 19.

---

### `SomeContext` Provider {/*provider*/}

Wrap your components into a context provider to specify the value of this context for all components inside:

```js
function App() {
  const [theme, setTheme] = useState('light');
  // ...
  return (
    <ThemeContext value={theme}>
      <Page />
    </ThemeContext>
  );
}
```

> **Note:**
>
> 
> 
> Starting in React 19, you can render `<SomeContext>` as a provider. 
> 
> In older versions of React, use `<SomeContext.Provider>`.
> 
> 


#### Props {/*provider-props*/}

* `value`: The value that you want to pass to all the components reading this context inside this provider, no matter how deep. The context value can be of any type. A component calling [`useContext(SomeContext)`](/reference/react/useContext) inside of the provider receives the `value` of the innermost corresponding context provider above it.

---

### `SomeContext.Consumer` {/*consumer*/}

Before `useContext` existed, there was an older way to read context:

```js
function Button() {
  // 🟡 Legacy way (not recommended)
  return (
    <ThemeContext.Consumer>
      {theme => (
        <button className={theme} />
      )}
    </ThemeContext.Consumer>
  );
}
```

Although this older way still works, **newly written code should read context with [`useContext()`](/reference/react/useContext) instead:**

```js
function Button() {
  // ✅ Recommended way
  const theme = useContext(ThemeContext);
  return <button className={theme} />;
}
```

#### Props {/*consumer-props*/}

* `children`: A function. React will call the function you pass with the current context value determined by the same algorithm as [`useContext()`](/reference/react/useContext) does, and render the result you return from this function. React will also re-run this function and update the UI whenever the context from the parent components changes.

---

## Usage {/*usage*/}

### Creating context {/*creating-context*/}

Context lets components [pass information deep down](/learn/passing-data-deeply-with-context) without explicitly passing props.

Call `createContext` outside any components to create one or more contexts.

```js [[1, 3, "ThemeContext"], [1, 4, "AuthContext"], [3, 3, "'light'"], [3, 4, "null"]]
import { createContext } from 'react';

const ThemeContext = createContext('light');
const AuthContext = createContext(null);
```

`createContext` returns a context object. Components can read context by passing it to [`useContext()`](/reference/react/useContext):

```js [[1, 2, "ThemeContext"], [1, 7, "AuthContext"]]
function Button() {
  const theme = useContext(ThemeContext);
  // ...
}

function Profile() {
  const currentUser = useContext(AuthContext);
  // ...
}
```

By default, the values they receive will be the default values you have specified when creating the contexts. However, by itself this isn't useful because the default values never change.

Context is useful because you can **provide other, dynamic values from your components:**

```js {8-9,11-12}
function App() {
  const [theme, setTheme] = useState('dark');
  const [currentUser, setCurrentUser] = useState({ name: 'Taylor' });

  // ...

  return (
    <ThemeContext value={theme}>
      <AuthContext value={currentUser}>
        <Page />
      </AuthContext>
    </ThemeContext>
  );
}
```

Now the `Page` component and any components inside it, no matter how deep, will "see" the passed context values. If the passed context values change, React will re-render the components reading the context as well.

[Read more about reading and providing context and see examples.](/reference/react/useContext)

---

### Importing and exporting context from a file {/*importing-and-exporting-context-from-a-file*/}

Often, components in different files will need access to the same context. This is why it's common to declare contexts in a separate file. Then you can use the [`export` statement](https://developer.mozilla.org/en-US/docs/web/javascript/reference/statements/export) to make context available for other files:

```js {4-5}
// Contexts.js
import { createContext } from 'react';

export const ThemeContext = createContext('light');
export const AuthContext = createContext(null);
```

Components declared in other files can then use the [`import`](https://developer.mozilla.org/en-US/docs/web/javascript/reference/statements/import) statement to read or provide this context:

```js {2}
// Button.js
import { ThemeContext } from './Contexts.js';

function Button() {
  const theme = useContext(ThemeContext);
  // ...
}
```

```js {2}
// App.js
import { ThemeContext, AuthContext } from './Contexts.js';

function App() {
  // ...
  return (
    <ThemeContext value={theme}>
      <AuthContext value={currentUser}>
        <Page />
      </AuthContext>
    </ThemeContext>
  );
}
```

This works similar to [importing and exporting components.](/learn/importing-and-exporting-components)

---

## Troubleshooting {/*troubleshooting*/}

### I can't find a way to change the context value {/*i-cant-find-a-way-to-change-the-context-value*/}


Code like this specifies the *default* context value:

```js
const ThemeContext = createContext('light');
```

This value never changes. React only uses this value as a fallback if it can't find a matching provider above.

To make context change over time, [add state and wrap components in a context provider.](/reference/react/useContext#updating-data-passed-via-context)
