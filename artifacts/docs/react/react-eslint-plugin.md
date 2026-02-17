---
title: React Eslint Plugin
source: react.dev
syllabus_weeks: [15]
topics: [eslint, eslint-plugin-react-hooks, rules of hooks, exhaustive-deps, purity, immutability, lint rules]
---



# Index

`eslint-plugin-react-hooks` provides ESLint rules to enforce the [Rules of React](/reference/rules).

This plugin helps you catch violations of React's rules at build time, ensuring your components and hooks follow React's rules for correctness and performance. The lints cover both fundamental React patterns (exhaustive-deps and rules-of-hooks) and issues flagged by React Compiler. React Compiler diagnostics are automatically surfaced by this ESLint plugin, and can be used even if your app hasn't adopted the compiler yet.

> **Note:**
>
> 
> When the compiler reports a diagnostic, it means that the compiler was able to statically detect a pattern that is not supported or breaks the Rules of React. When it detects this, it **automatically** skips over those components and hooks, while keeping the rest of your app compiled. This ensures optimal coverage of safe optimizations that won't break your app.
> 
> What this means for linting, is that you don’t need to fix all violations immediately. Address them at your own pace to gradually increase the number of optimized components.
> 


## Recommended Rules {/*recommended*/}

These rules are included in the `recommended` preset in `eslint-plugin-react-hooks`:

* [`exhaustive-deps`](/reference/eslint-plugin-react-hooks/lints/exhaustive-deps) - Validates that dependency arrays for React hooks contain all necessary dependencies
* [`rules-of-hooks`](/reference/eslint-plugin-react-hooks/lints/rules-of-hooks) - Validates that components and hooks follow the Rules of Hooks
* [`component-hook-factories`](/reference/eslint-plugin-react-hooks/lints/component-hook-factories) - Validates higher order functions defining nested components or hooks
* [`config`](/reference/eslint-plugin-react-hooks/lints/config) - Validates the compiler configuration options
* [`error-boundaries`](/reference/eslint-plugin-react-hooks/lints/error-boundaries) - Validates usage of Error Boundaries instead of try/catch for child errors
* [`gating`](/reference/eslint-plugin-react-hooks/lints/gating) - Validates configuration of gating mode
* [`globals`](/reference/eslint-plugin-react-hooks/lints/globals) - Validates against assignment/mutation of globals during render
* [`immutability`](/reference/eslint-plugin-react-hooks/lints/immutability) - Validates against mutating props, state, and other immutable values
* [`incompatible-library`](/reference/eslint-plugin-react-hooks/lints/incompatible-library) - Validates against usage of libraries which are incompatible with memoization
* [`preserve-manual-memoization`](/reference/eslint-plugin-react-hooks/lints/preserve-manual-memoization) - Validates that existing manual memoization is preserved by the compiler
* [`purity`](/reference/eslint-plugin-react-hooks/lints/purity) - Validates that components/hooks are pure by checking known-impure functions
* [`refs`](/reference/eslint-plugin-react-hooks/lints/refs) - Validates correct usage of refs, not reading/writing during render
* [`set-state-in-effect`](/reference/eslint-plugin-react-hooks/lints/set-state-in-effect) - Validates against calling setState synchronously in an effect
* [`set-state-in-render`](/reference/eslint-plugin-react-hooks/lints/set-state-in-render) - Validates against setting state during render
* [`static-components`](/reference/eslint-plugin-react-hooks/lints/static-components) - Validates that components are static, not recreated every render
* [`unsupported-syntax`](/reference/eslint-plugin-react-hooks/lints/unsupported-syntax) - Validates against syntax that React Compiler does not support
* [`use-memo`](/reference/eslint-plugin-react-hooks/lints/use-memo) - Validates usage of the `useMemo` hook without a return value

# Exhaustive Deps

Validates that dependency arrays for React hooks contain all necessary dependencies.

## Rule Details {/*rule-details*/}

React hooks like `useEffect`, `useMemo`, and `useCallback` accept dependency arrays. When a value referenced inside these hooks isn't included in the dependency array, React won't re-run the effect or recalculate the value when that dependency changes. This causes stale closures where the hook uses outdated values.

## Common Violations {/*common-violations*/}

This error often happens when you try to "trick" React about dependencies to control when an effect runs. Effects should synchronize your component with external systems. The dependency array tells React which values the effect uses, so React knows when to re-synchronize.

If you find yourself fighting with the linter, you likely need to restructure your code. See [Removing Effect Dependencies](/learn/removing-effect-dependencies) to learn how.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Missing dependency
useEffect(() => {
  console.log(count);
}, []); // Missing 'count'

// ❌ Missing prop
useEffect(() => {
  fetchUser(userId);
}, []); // Missing 'userId'

// ❌ Incomplete dependencies
useMemo(() => {
  return items.sort(sortOrder);
}, [items]); // Missing 'sortOrder'
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ All dependencies included
useEffect(() => {
  console.log(count);
}, [count]);

// ✅ All dependencies included
useEffect(() => {
  fetchUser(userId);
}, [userId]);
```

## Troubleshooting {/*troubleshooting*/}

### Adding a function dependency causes infinite loops {/*function-dependency-loops*/}

You have an effect, but you're creating a new function on every render:

```js
// ❌ Causes infinite loop
const logItems = () => {
  console.log(items);
};

useEffect(() => {
  logItems();
}, [logItems]); // Infinite loop!
```

In most cases, you don't need the effect. Call the function where the action happens instead:

```js
// ✅ Call it from the event handler
const logItems = () => {
  console.log(items);
};

return <button onClick={logItems}>Log</button>;

// ✅ Or derive during render if there's no side effect
items.forEach(item => {
  console.log(item);
});
```

If you genuinely need the effect (for example, to subscribe to something external), make the dependency stable:

```js
// ✅ useCallback keeps the function reference stable
const logItems = useCallback(() => {
  console.log(items);
}, [items]);

useEffect(() => {
  logItems();
}, [logItems]);

// ✅ Or move the logic straight into the effect
useEffect(() => {
  console.log(items);
}, [items]);
```

### Running an effect only once {/*effect-on-mount*/}

You want to run an effect once on mount, but the linter complains about missing dependencies:

```js
// ❌ Missing dependency
useEffect(() => {
  sendAnalytics(userId);
}, []); // Missing 'userId'
```

Either include the dependency (recommended) or use a ref if you truly need to run once:

```js
// ✅ Include dependency
useEffect(() => {
  sendAnalytics(userId);
}, [userId]);

// ✅ Or use a ref guard inside an effect
const sent = useRef(false);

useEffect(() => {
  if (sent.current) {
    return;
  }

  sent.current = true;
  sendAnalytics(userId);
}, [userId]);
```

## Options {/*options*/}

You can configure custom effect hooks using shared ESLint settings (available in `eslint-plugin-react-hooks` 6.1.1 and later):

```js
{
  "settings": {
    "react-hooks": {
      "additionalEffectHooks": "(useMyEffect|useCustomEffect)"
    }
  }
}
```

- `additionalEffectHooks`: Regex pattern matching custom hooks that should be checked for exhaustive dependencies. This configuration is shared across all `react-hooks` rules.

For backward compatibility, this rule also accepts a rule-level option:

```js
{
  "rules": {
    "react-hooks/exhaustive-deps": ["warn", {
      "additionalHooks": "(useMyCustomHook|useAnotherHook)"
    }]
  }
}
```

- `additionalHooks`: Regex for hooks that should be checked for exhaustive dependencies. **Note:** If this rule-level option is specified, it takes precedence over the shared `settings` configuration.


# Set State In Render

Validates against unconditionally setting state during render, which can trigger additional renders and potential infinite render loops.

## Rule Details {/*rule-details*/}

Calling `setState` during render unconditionally triggers another render before the current one finishes. This creates an infinite loop that crashes your app.

## Common Violations {/*common-violations*/}

### Invalid {/*invalid*/}

```js {expectedErrors: {'react-compiler': [4]}}
// ❌ Unconditional setState directly in render
function Component({value}) {
  const [count, setCount] = useState(0);
  setCount(value); // Infinite loop!
  return <div>{count}</div>;
}
```

### Valid {/*valid*/}

```js
// ✅ Derive during render
function Component({items}) {
  const sorted = [...items].sort(); // Just calculate it in render
  return <ul>{sorted.map(/*...*/)}</ul>;
}

// ✅ Set state in event handler
function Component() {
  const [count, setCount] = useState(0);
  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}

// ✅ Derive from props instead of setting state
function Component({user}) {
  const name = user?.name || '';
  const email = user?.email || '';
  return <div>{name}</div>;
}

// ✅ Conditionally derive state from props and state from previous renders
function Component({ items }) {
  const [isReverse, setIsReverse] = useState(false);
  const [selection, setSelection] = useState(null);

  const [prevItems, setPrevItems] = useState(items);
  if (items !== prevItems) { // This condition makes it valid
    setPrevItems(items);
    setSelection(null);
  }
  // ...
}
```

## Troubleshooting {/*troubleshooting*/}

### I want to sync state to a prop {/*clamp-state-to-prop*/}

A common problem is trying to "fix" state after it renders. Suppose you want to keep a counter from exceeding a `max` prop:

```js
// ❌ Wrong: clamps during render
function Counter({max}) {
  const [count, setCount] = useState(0);

  if (count > max) {
    setCount(max);
  }

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

As soon as `count` exceeds `max`, an infinite loop is triggered.

Instead, it's often better to move this logic to the event (the place where the state is first set). For example, you can enforce the maximum at the moment you update state:

```js
// ✅ Clamp when updating
function Counter({max}) {
  const [count, setCount] = useState(0);

  const increment = () => {
    setCount(current => Math.min(current + 1, max));
  };

  return <button onClick={increment}>{count}</button>;
}
```

Now the setter only runs in response to the click, React finishes the render normally, and `count` never crosses `max`.

In rare cases, you may need to adjust state based on information from previous renders. For those, follow [this pattern](https://react.dev/reference/react/useState#storing-information-from-previous-renders) of setting state conditionally.


# Error Boundaries

Validates usage of Error Boundaries instead of try/catch for errors in child components.

## Rule Details {/*rule-details*/}

Try/catch blocks can't catch errors that happen during React's rendering process. Errors thrown in rendering methods or hooks bubble up through the component tree. Only [Error Boundaries](/reference/react/Component#catching-rendering-errors-with-an-error-boundary) can catch these errors.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js {expectedErrors: {'react-compiler': [4]}}
// ❌ Try/catch won't catch render errors
function Parent() {
  try {
    return <ChildComponent />; // If this throws, catch won't help
  } catch (error) {
    return <div>Error occurred</div>;
  }
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Using error boundary
function Parent() {
  return (
    <ErrorBoundary>
      <ChildComponent />
    </ErrorBoundary>
  );
}
```

## Troubleshooting {/*troubleshooting*/}

### Why is the linter telling me not to wrap `use` in `try`/`catch`? {/*why-is-the-linter-telling-me-not-to-wrap-use-in-trycatch*/}

The `use` hook doesn't throw errors in the traditional sense, it suspends component execution. When `use` encounters a pending promise, it suspends the component and lets React show a fallback. Only Suspense and Error Boundaries can handle these cases. The linter warns against `try`/`catch` around `use` to prevent confusion as the `catch` block would never run.

```js {expectedErrors: {'react-compiler': [5]}}
// ❌ Try/catch around `use` hook
function Component({promise}) {
  try {
    const data = use(promise); // Won't catch - `use` suspends, not throws
    return <div>{data}</div>;
  } catch (error) {
    return <div>Failed to load</div>; // Unreachable
  }
}

// ✅ Error boundary catches `use` errors
function App() {
  return (
    <ErrorBoundary fallback={<div>Failed to load</div>}>
      <Suspense fallback={<div>Loading...</div>}>
        <DataComponent promise={fetchData()} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

# Gating

Validates configuration of [gating mode](/reference/react-compiler/gating).

## Rule Details {/*rule-details*/}

Gating mode lets you gradually adopt React Compiler by marking specific components for optimization. This rule ensures your gating configuration is valid so the compiler knows which components to process.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Missing required fields
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      gating: {
        importSpecifierName: '__experimental_useCompiler'
        // Missing 'source' field
      }
    }]
  ]
};

// ❌ Invalid gating type
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      gating: '__experimental_useCompiler' // Should be object
    }]
  ]
};
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Complete gating configuration
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      gating: {
        importSpecifierName: 'isCompilerEnabled', // exported function name
        source: 'featureFlags' // module name
      }
    }]
  ]
};

// featureFlags.js
export function isCompilerEnabled() {
  // ...
}

// ✅ No gating (compile everything)
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      // No gating field - compiles all components
    }]
  ]
};
```


# Immutability

Validates against mutating props, state, and other values that [are immutable](/reference/rules/components-and-hooks-must-be-pure#props-and-state-are-immutable).

## Rule Details {/*rule-details*/}

A component’s props and state are immutable snapshots. Never mutate them directly. Instead, pass new props down, and use the setter function from `useState`.

## Common Violations {/*common-violations*/}

### Invalid {/*invalid*/}

```js
// ❌ Array push mutation
function Component() {
  const [items, setItems] = useState([1, 2, 3]);

  const addItem = () => {
    items.push(4); // Mutating!
    setItems(items); // Same reference, no re-render
  };
}

// ❌ Object property assignment
function Component() {
  const [user, setUser] = useState({name: 'Alice'});

  const updateName = () => {
    user.name = 'Bob'; // Mutating!
    setUser(user); // Same reference
  };
}

// ❌ Sort without spreading
function Component() {
  const [items, setItems] = useState([3, 1, 2]);

  const sortItems = () => {
    setItems(items.sort()); // sort mutates!
  };
}
```

### Valid {/*valid*/}

```js
// ✅ Create new array
function Component() {
  const [items, setItems] = useState([1, 2, 3]);

  const addItem = () => {
    setItems([...items, 4]); // New array
  };
}

// ✅ Create new object
function Component() {
  const [user, setUser] = useState({name: 'Alice'});

  const updateName = () => {
    setUser({...user, name: 'Bob'}); // New object
  };
}
```

## Troubleshooting {/*troubleshooting*/}

### I need to add items to an array {/*add-items-array*/}

Mutating arrays with methods like `push()` won't trigger re-renders:

```js
// ❌ Wrong: Mutating the array
function TodoList() {
  const [todos, setTodos] = useState([]);

  const addTodo = (id, text) => {
    todos.push({id, text});
    setTodos(todos); // Same array reference!
  };

  return (
    <ul>
      {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
    </ul>
  );
}
```

Create a new array instead:

```js
// ✅ Better: Create a new array
function TodoList() {
  const [todos, setTodos] = useState([]);

  const addTodo = (id, text) => {
    setTodos([...todos, {id, text}]);
    // Or: setTodos(todos => [...todos, {id: Date.now(), text}])
  };

  return (
    <ul>
      {todos.map(todo => <li key={todo.id}>{todo.text}</li>)}
    </ul>
  );
}
```

### I need to update nested objects {/*update-nested-objects*/}

Mutating nested properties doesn't trigger re-renders:

```js
// ❌ Wrong: Mutating nested object
function UserProfile() {
  const [user, setUser] = useState({
    name: 'Alice',
    settings: {
      theme: 'light',
      notifications: true
    }
  });

  const toggleTheme = () => {
    user.settings.theme = 'dark'; // Mutation!
    setUser(user); // Same object reference
  };
}
```

Spread at each level that needs updating:

```js
// ✅ Better: Create new objects at each level
function UserProfile() {
  const [user, setUser] = useState({
    name: 'Alice',
    settings: {
      theme: 'light',
      notifications: true
    }
  });

  const toggleTheme = () => {
    setUser({
      ...user,
      settings: {
        ...user.settings,
        theme: 'dark'
      }
    });
  };
}
```

# Set State In Effect

Validates against calling setState synchronously in an effect, which can lead to re-renders that degrade performance.

## Rule Details {/*rule-details*/}

Setting state immediately inside an effect forces React to restart the entire render cycle. When you update state in an effect, React must re-render your component, apply changes to the DOM, and then run effects again. This creates an extra render pass that could have been avoided by transforming data directly during render or deriving state from props. Transform data at the top level of your component instead. This code will naturally re-run when props or state change without triggering additional render cycles.

Synchronous `setState` calls in effects trigger immediate re-renders before the browser can paint, causing performance issues and visual jank. React has to render twice: once to apply the state update, then again after effects run. This double rendering is wasteful when the same result could be achieved with a single render.

In many cases, you may also not need an effect at all. Please see [You Might Not Need an Effect](/learn/you-might-not-need-an-effect) for more information.

## Common Violations {/*common-violations*/}

This rule catches several patterns where synchronous setState is used unnecessarily:

- Setting loading state synchronously
- Deriving state from props in effects
- Transforming data in effects instead of render

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Synchronous setState in effect
function Component({data}) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    setItems(data); // Extra render, use initial state instead
  }, [data]);
}

// ❌ Setting loading state synchronously
function Component() {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true); // Synchronous, causes extra render
    fetchData().then(() => setLoading(false));
  }, []);
}

// ❌ Transforming data in effect
function Component({rawData}) {
  const [processed, setProcessed] = useState([]);

  useEffect(() => {
    setProcessed(rawData.map(transform)); // Should derive in render
  }, [rawData]);
}

// ❌ Deriving state from props
function Component({selectedId, items}) {
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    setSelected(items.find(i => i.id === selectedId));
  }, [selectedId, items]);
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ setState in an effect is fine if the value comes from a ref
function Tooltip() {
  const ref = useRef(null);
  const [tooltipHeight, setTooltipHeight] = useState(0);

  useLayoutEffect(() => {
    const { height } = ref.current.getBoundingClientRect();
    setTooltipHeight(height);
  }, []);
}

// ✅ Calculate during render
function Component({selectedId, items}) {
  const selected = items.find(i => i.id === selectedId);
  return <div>{selected?.name}</div>;
}
```

**When something can be calculated from the existing props or state, don't put it in state.** Instead, calculate it during rendering. This makes your code faster, simpler, and less error-prone. Learn more in [You Might Not Need an Effect](/learn/you-might-not-need-an-effect).


# Use Memo

Validates that the `useMemo` hook is used with a return value. See [`useMemo` docs](/reference/react/useMemo) for more information.

## Rule Details {/*rule-details*/}

`useMemo` is for computing and caching expensive values, not for side effects. Without a return value, `useMemo` returns `undefined`, which defeats its purpose and likely indicates you're using the wrong hook.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js {expectedErrors: {'react-compiler': [3]}}
// ❌ No return value
function Component({ data }) {
  const processed = useMemo(() => {
    data.forEach(item => console.log(item));
    // Missing return!
  }, [data]);

  return <div>{processed}</div>; // Always undefined
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Returns computed value
function Component({ data }) {
  const processed = useMemo(() => {
    return data.map(item => item * 2);
  }, [data]);

  return <div>{processed}</div>;
}
```

## Troubleshooting {/*troubleshooting*/}

### I need to run side effects when dependencies change {/*side-effects*/}

You might try to use `useMemo` for side effects:

{/* TODO(@poteto) fix compiler validation to check for unassigned useMemos */}
```js {expectedErrors: {'react-compiler': [4]}}
// ❌ Wrong: Side effects in useMemo
function Component({user}) {
  // No return value, just side effect
  useMemo(() => {
    analytics.track('UserViewed', {userId: user.id});
  }, [user.id]);

  // Not assigned to a variable
  useMemo(() => {
    return analytics.track('UserViewed', {userId: user.id});
  }, [user.id]);
}
```

If the side effect needs to happen in response to user interaction, it's best to colocate the side effect with the event:

```js
// ✅ Good: Side effects in event handlers
function Component({user}) {
  const handleClick = () => {
    analytics.track('ButtonClicked', {userId: user.id});
    // Other click logic...
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

If the side effect sychronizes React state with some external state (or vice versa), use `useEffect`:

```js
// ✅ Good: Synchronization in useEffect
function Component({theme}) {
  useEffect(() => {
    localStorage.setItem('preferredTheme', theme);
    document.body.className = theme;
  }, [theme]);

  return <div>Current theme: {theme}</div>;
}
```


# Static Components

Validates that components are static, not recreated every render. Components that are recreated dynamically can reset state and trigger excessive re-rendering.

## Rule Details {/*rule-details*/}

Components defined inside other components are recreated on every render. React sees each as a brand new component type, unmounting the old one and mounting the new one, destroying all state and DOM nodes in the process.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Component defined inside component
function Parent() {
  const ChildComponent = () => { // New component every render!
    const [count, setCount] = useState(0);
    return <button onClick={() => setCount(count + 1)}>{count}</button>;
  };

  return <ChildComponent />; // State resets every render
}

// ❌ Dynamic component creation
function Parent({type}) {
  const Component = type === 'button'
    ? () => <button>Click</button>
    : () => <div>Text</div>;

  return <Component />;
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Components at module level
const ButtonComponent = () => <button>Click</button>;
const TextComponent = () => <div>Text</div>;

function Parent({type}) {
  const Component = type === 'button'
    ? ButtonComponent  // Reference existing component
    : TextComponent;

  return <Component />;
}
```

## Troubleshooting {/*troubleshooting*/}

### I need to render different components conditionally {/*conditional-components*/}

You might define components inside to access local state:

```js {expectedErrors: {'react-compiler': [13]}}
// ❌ Wrong: Inner component to access parent state
function Parent() {
  const [theme, setTheme] = useState('light');

  function ThemedButton() { // Recreated every render!
    return (
      <button className={theme}>
        Click me
      </button>
    );
  }

  return <ThemedButton />;
}
```

Pass data as props instead:

```js
// ✅ Better: Pass props to static component
function ThemedButton({theme}) {
  return (
    <button className={theme}>
      Click me
    </button>
  );
}

function Parent() {
  const [theme, setTheme] = useState('light');
  return <ThemedButton theme={theme} />;
}
```

> **Note:**
>
> 
> 
> If you find yourself wanting to define components inside other components to access local variables, that's a sign you should be passing props instead. This makes components more reusable and testable.
> 
> 


# Component Hook Factories

Validates against higher order functions defining nested components or hooks. Components and hooks should be defined at the module level.

## Rule Details {/*rule-details*/}

Defining components or hooks inside other functions creates new instances on every call. React treats each as a completely different component, destroying and recreating the entire component tree, losing all state, and causing performance problems.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js {expectedErrors: {'react-compiler': [14]}}
// ❌ Factory function creating components
function createComponent(defaultValue) {
  return function Component() {
    // ...
  };
}

// ❌ Component defined inside component
function Parent() {
  function Child() {
    // ...
  }

  return <Child />;
}

// ❌ Hook factory function
function createCustomHook(endpoint) {
  return function useData() {
    // ...
  };
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Component defined at module level
function Component({ defaultValue }) {
  // ...
}

// ✅ Custom hook at module level
function useData(endpoint) {
  // ...
}
```

## Troubleshooting {/*troubleshooting*/}

### I need dynamic component behavior {/*dynamic-behavior*/}

You might think you need a factory to create customized components:

```js
// ❌ Wrong: Factory pattern
function makeButton(color) {
  return function Button({children}) {
    return (
      <button style={{backgroundColor: color}}>
        {children}
      </button>
    );
  };
}

const RedButton = makeButton('red');
const BlueButton = makeButton('blue');
```

Pass [JSX as children](/learn/passing-props-to-a-component#passing-jsx-as-children) instead:

```js
// ✅ Better: Pass JSX as children
function Button({color, children}) {
  return (
    <button style={{backgroundColor: color}}>
      {children}
    </button>
  );
}

function App() {
  return (
    <>
      <Button color="red">Red</Button>
      <Button color="blue">Blue</Button>
    </>
  );
}
```


# Incompatible Library

Validates against usage of libraries which are incompatible with memoization (manual or automatic).

> **Note:**
>
> 
> 
> These libraries were designed before React's memoization rules were fully documented. They made the correct choices at the time to optimize for ergonomic ways to keep components just the right amount of reactive as app state changes. While these legacy patterns worked, we have since discovered that it's incompatible with React's programming model. We will continue working with library authors to migrate these libraries to use patterns that follow the Rules of React.
> 
> 


## Rule Details {/*rule-details*/}

Some libraries use patterns that aren't supported by React. When the linter detects usages of these APIs from a [known list](https://github.com/facebook/react/blob/main/compiler/packages/babel-plugin-react-compiler/src/HIR/DefaultModuleTypeProvider.ts), it flags them under this rule. This means that React Compiler can automatically skip over components that use these incompatible APIs, in order to avoid breaking your app.

```js
// Example of how memoization breaks with these libraries
function Form() {
  const { watch } = useForm();

  // ❌ This value will never update, even when 'name' field changes
  const name = useMemo(() => watch('name'), [watch]);

  return <div>Name: {name}</div>; // UI appears "frozen"
}
```

React Compiler automatically memoizes values following the Rules of React. If something breaks with manual `useMemo`, it will also break the compiler's automatic optimization. This rule helps identify these problematic patterns.

> **Deep Dive: Designing APIs that follow the Rules of React {/*designing-apis-that-follow-the-rules-of-react*/}**
>
> One question to think about when designing a library API or hook is whether calling the API can be safely memoized with `useMemo`. If it can't, then both manual and React Compiler memoizations will break your user's code.
> 
> For example, one such incompatible pattern is "interior mutability". Interior mutability is when an object or function keeps its own hidden state that changes over time, even though the reference to it stays the same. Think of it like a box that looks the same on the outside but secretly rearranges its contents. React can't tell anything changed because it only checks if you gave it a different box, not what's inside. This breaks memoization, since React relies on the outer object (or function) changing if part of its value has changed.
> 
> As a rule of thumb, when designing React APIs, think about whether `useMemo` would break it:
> 
> ```js
> function Component() {
>   const { someFunction } = useLibrary();
>   // it should always be safe to memoize functions like this
>   const result = useMemo(() => someFunction(), [someFunction]);
> }
> ```
> 
> Instead, design APIs that return immutable state and use explicit update functions:
> 
> ```js
> // ✅ Good: Return immutable state that changes reference when updated
> function Component() {
>   const { field, updateField } = useLibrary();
>   // this is always safe to memo
>   const greeting = useMemo(() => `Hello, ${field.name}!`, [field.name]);
> 
>   return (
>     <div>
>       <input
>         value={field.name}
>         onChange={(e) => updateField('name', e.target.value)}
>       />
>       <p>{greeting}</p>
>     </div>
>   );
> }
> ```


### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ react-hook-form `watch`
function Component() {
  const {watch} = useForm();
  const value = watch('field'); // Interior mutability
  return <div>{value}</div>;
}

// ❌ TanStack Table `useReactTable`
function Component({data}) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
  // table instance uses interior mutability
  return <Table table={table} />;
}
```

> **Pitfall: MobX {/*mobx*/}**
>
> MobX patterns like `observer` also break memoization assumptions, but the linter does not yet detect them. If you rely on MobX and find that your app doesn't work with React Compiler, you may need to use the `"use no memo" directive`.
> 
> ```js
> // ❌ MobX `observer`
> const Component = observer(() => {
>   const [timer] = useState(() => new Timer());
>   return <span>Seconds passed: {timer.secondsPassed}</span>;
> });
> ```


### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ For react-hook-form, use `useWatch`:
function Component() {
  const {register, control} = useForm();
  const watchedValue = useWatch({
    control,
    name: 'field'
  });

  return (
    <>
      <input {...register('field')} />
      <div>Current value: {watchedValue}</div>
    </>
  );
}
```

Some other libraries do not yet have alternative APIs that are compatible with React's memoization model. If the linter doesn't automatically skip over your components or hooks that call these APIs, please [file an issue](https://github.com/facebook/react/issues) so we can add it to the linter.


# Preserve Manual Memoization

Validates that existing manual memoization is preserved by the compiler. React Compiler will only compile components and hooks if its inference [matches or exceeds the existing manual memoization](/learn/react-compiler/introduction#what-should-i-do-about-usememo-usecallback-and-reactmemo).

## Rule Details {/*rule-details*/}

React Compiler preserves your existing `useMemo`, `useCallback`, and `React.memo` calls. If you've manually memoized something, the compiler assumes you had a good reason and won't remove it. However, incomplete dependencies prevent the compiler from understanding your code's data flow and applying further optimizations.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Missing dependencies in useMemo
function Component({ data, filter }) {
  const filtered = useMemo(
    () => data.filter(filter),
    [data] // Missing 'filter' dependency
  );

  return <List items={filtered} />;
}

// ❌ Missing dependencies in useCallback
function Component({ onUpdate, value }) {
  const handleClick = useCallback(() => {
    onUpdate(value);
  }, [onUpdate]); // Missing 'value'

  return <button onClick={handleClick}>Update</button>;
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Complete dependencies
function Component({ data, filter }) {
  const filtered = useMemo(
    () => data.filter(filter),
    [data, filter] // All dependencies included
  );

  return <List items={filtered} />;
}

// ✅ Or let the compiler handle it
function Component({ data, filter }) {
  // No manual memoization needed
  const filtered = data.filter(filter);
  return <List items={filtered} />;
}
```

## Troubleshooting {/*troubleshooting*/}

### Should I remove my manual memoization? {/*remove-manual-memoization*/}

You might wonder if React Compiler makes manual memoization unnecessary:

```js
// Do I still need this?
function Component({items, sortBy}) {
  const sorted = useMemo(() => {
    return [...items].sort((a, b) => {
      return a[sortBy] - b[sortBy];
    });
  }, [items, sortBy]);

  return <List items={sorted} />;
}
```

You can safely remove it if using React Compiler:

```js
// ✅ Better: Let the compiler optimize
function Component({items, sortBy}) {
  const sorted = [...items].sort((a, b) => {
    return a[sortBy] - b[sortBy];
  });

  return <List items={sorted} />;
}
```

# Unsupported Syntax

Validates against syntax that React Compiler does not support. If you need to, you can still use this syntax outside of React, such as in a standalone utility function.

## Rule Details {/*rule-details*/}

React Compiler needs to statically analyze your code to apply optimizations. Features like `eval` and `with` make it impossible to statically understand what the code does at compile time, so the compiler can't optimize components that use them.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Using eval in component
function Component({ code }) {
  const result = eval(code); // Can't be analyzed
  return <div>{result}</div>;
}

// ❌ Using with statement
function Component() {
  with (Math) { // Changes scope dynamically
    return <div>{sin(PI / 2)}</div>;
  }
}

// ❌ Dynamic property access with eval
function Component({propName}) {
  const value = eval(`props.${propName}`);
  return <div>{value}</div>;
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Use normal property access
function Component({propName, props}) {
  const value = props[propName]; // Analyzable
  return <div>{value}</div>;
}

// ✅ Use standard Math methods
function Component() {
  return <div>{Math.sin(Math.PI / 2)}</div>;
}
```

## Troubleshooting {/*troubleshooting*/}

### I need to evaluate dynamic code {/*evaluate-dynamic-code*/}

You might need to evaluate user-provided code:

```js {expectedErrors: {'react-compiler': [3]}}
// ❌ Wrong: eval in component
function Calculator({expression}) {
  const result = eval(expression); // Unsafe and unoptimizable
  return <div>Result: {result}</div>;
}
```

Use a safe expression parser instead:

```js
// ✅ Better: Use a safe parser
import {evaluate} from 'mathjs'; // or similar library

function Calculator({expression}) {
  const [result, setResult] = useState(null);

  const calculate = () => {
    try {
      // Safe mathematical expression evaluation
      setResult(evaluate(expression));
    } catch (error) {
      setResult('Invalid expression');
    }
  };

  return (
    <div>
      <button onClick={calculate}>Calculate</button>
      {result && <div>Result: {result}</div>}
    </div>
  );
}
```

> **Note:**
>
> 
> 
> Never use `eval` with user input - it's a security risk. Use dedicated parsing libraries for specific use cases like mathematical expressions, JSON parsing, or template evaluation.
> 
> 


# Refs

Validates correct usage of refs, not reading/writing during render. See the "pitfalls" section in [`useRef()` usage](/reference/react/useRef#usage).

## Rule Details {/*rule-details*/}

Refs hold values that aren't used for rendering. Unlike state, changing a ref doesn't trigger a re-render. Reading or writing `ref.current` during render breaks React's expectations. Refs might not be initialized when you try to read them, and their values can be stale or inconsistent.

## How It Detects Refs {/*how-it-detects-refs*/}

The lint only applies these rules to values it knows are refs. A value is inferred as a ref when the compiler sees any of the following patterns:

- Returned from `useRef()` or `React.createRef()`.

  ```js
  const scrollRef = useRef(null);
  ```

- An identifier named `ref` or ending in `Ref` that reads from or writes to `.current`.

  ```js
  buttonRef.current = node;
  ```

- Passed through a JSX `ref` prop (for example `<div ref={someRef} />`).

  ```jsx
  <input ref={inputRef} />
  ```

Once something is marked as a ref, that inference follows the value through assignments, destructuring, or helper calls. This lets the lint surface violations even when `ref.current` is accessed inside another function that received the ref as an argument.

## Common Violations {/*common-violations*/}

- Reading `ref.current` during render
- Updating `refs` during render
- Using `refs` for values that should be state

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Reading ref during render
function Component() {
  const ref = useRef(0);
  const value = ref.current; // Don't read during render
  return <div>{value}</div>;
}

// ❌ Modifying ref during render
function Component({value}) {
  const ref = useRef(null);
  ref.current = value; // Don't modify during render
  return <div />;
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Read ref in effects/handlers
function Component() {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      console.log(ref.current.offsetWidth); // OK in effect
    }
  });

  return <div ref={ref} />;
}

// ✅ Use state for UI values
function Component() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}

// ✅ Lazy initialization of ref value
function Component() {
  const ref = useRef(null);

  // Initialize only once on first use
  if (ref.current === null) {
    ref.current = expensiveComputation(); // OK - lazy initialization
  }

  const handleClick = () => {
    console.log(ref.current); // Use the initialized value
  };

  return <button onClick={handleClick}>Click</button>;
}
```

## Troubleshooting {/*troubleshooting*/}

### The lint flagged my plain object with `.current` {/*plain-object-current*/}

The name heuristic intentionally treats `ref.current` and `fooRef.current` as real refs. If you're modeling a custom container object, pick a different name (for example, `box`) or move the mutable value into state. Renaming avoids the lint because the compiler stops inferring it as a ref.


# Globals

Validates against assignment/mutation of globals during render, part of ensuring that [side effects must run outside of render](/reference/rules/components-and-hooks-must-be-pure#side-effects-must-run-outside-of-render).

## Rule Details {/*rule-details*/}

Global variables exist outside React's control. When you modify them during render, you break React's assumption that rendering is pure. This can cause components to behave differently in development vs production, break Fast Refresh, and make your app impossible to optimize with features like React Compiler.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Global counter
let renderCount = 0;
function Component() {
  renderCount++; // Mutating global
  return <div>Count: {renderCount}</div>;
}

// ❌ Modifying window properties
function Component({userId}) {
  window.currentUser = userId; // Global mutation
  return <div>User: {userId}</div>;
}

// ❌ Global array push
const events = [];
function Component({event}) {
  events.push(event); // Mutating global array
  return <div>Events: {events.length}</div>;
}

// ❌ Cache manipulation
const cache = {};
function Component({id}) {
  if (!cache[id]) {
    cache[id] = fetchData(id); // Modifying cache during render
  }
  return <div>{cache[id]}</div>;
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Use state for counters
function Component() {
  const [clickCount, setClickCount] = useState(0);

  const handleClick = () => {
    setClickCount(c => c + 1);
  };

  return (
    <button onClick={handleClick}>
      Clicked: {clickCount} times
    </button>
  );
}

// ✅ Use context for global values
function Component() {
  const user = useContext(UserContext);
  return <div>User: {user.id}</div>;
}

// ✅ Synchronize external state with React
function Component({title}) {
  useEffect(() => {
    document.title = title; // OK in effect
  }, [title]);

  return <div>Page: {title}</div>;
}
```


# Purity

Validates that [components/hooks are pure](/reference/rules/components-and-hooks-must-be-pure) by checking that they do not call known-impure functions.

## Rule Details {/*rule-details*/}

React components must be pure functions - given the same props, they should always return the same JSX. When components use functions like `Math.random()` or `Date.now()` during render, they produce different output each time, breaking React's assumptions and causing bugs like hydration mismatches, incorrect memoization, and unpredictable behavior.

## Common Violations {/*common-violations*/}

In general, any API that returns a different value for the same inputs violates this rule. Usual examples include:

- `Math.random()`
- `Date.now()` / `new Date()`
- `crypto.randomUUID()`
- `performance.now()`

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Math.random() in render
function Component() {
  const id = Math.random(); // Different every render
  return <div key={id}>Content</div>;
}

// ❌ Date.now() for values
function Component() {
  const timestamp = Date.now(); // Changes every render
  return <div>Created at: {timestamp}</div>;
}
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Stable IDs from initial state
function Component() {
  const [id] = useState(() => crypto.randomUUID());
  return <div key={id}>Content</div>;
}
```

## Troubleshooting {/*troubleshooting*/}

### I need to show the current time {/*current-time*/}

Calling `Date.now()` during render makes your component impure:

```js {expectedErrors: {'react-compiler': [3]}}
// ❌ Wrong: Time changes every render
function Clock() {
  return <div>Current time: {Date.now()}</div>;
}
```

Instead, [move the impure function outside of render](/reference/rules/components-and-hooks-must-be-pure#components-and-hooks-must-be-idempotent):

```js
function Clock() {
  const [time, setTime] = useState(() => Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(Date.now());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <div>Current time: {time}</div>;
}
```

# Config

Validates the compiler [configuration options](/reference/react-compiler/configuration).

## Rule Details {/*rule-details*/}

React Compiler accepts various [configuration options](/reference/react-compiler/configuration)  to control its behavior. This rule validates that your configuration uses correct option names and value types, preventing silent failures from typos or incorrect settings.

### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Unknown option name
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      compileMode: 'all' // Typo: should be compilationMode
    }]
  ]
};

// ❌ Invalid option value
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      compilationMode: 'everything' // Invalid: use 'all' or 'infer'
    }]
  ]
};
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
// ✅ Valid compiler configuration
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      compilationMode: 'infer',
      panicThreshold: 'critical_errors'
    }]
  ]
};
```

## Troubleshooting {/*troubleshooting*/}

### Configuration not working as expected {/*config-not-working*/}

Your compiler configuration might have typos or incorrect values:

```js
// ❌ Wrong: Common configuration mistakes
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      // Typo in option name
      compilationMod: 'all',
      // Wrong value type
      panicThreshold: true,
      // Unknown option
      optimizationLevel: 'max'
    }]
  ]
};
```

Check the [configuration documentation](/reference/react-compiler/configuration) for valid options:

```js
// ✅ Better: Valid configuration
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      compilationMode: 'all', // or 'infer'
      panicThreshold: 'none', // or 'critical_errors', 'all_errors'
      // Only use documented options
    }]
  ]
};
```


# Rules Of Hooks

Validates that components and hooks follow the [Rules of Hooks](/reference/rules/rules-of-hooks).

## Rule Details {/*rule-details*/}

React relies on the order in which hooks are called to correctly preserve state between renders. Each time your component renders, React expects the exact same hooks to be called in the exact same order. When hooks are called conditionally or in loops, React loses track of which state corresponds to which hook call, leading to bugs like state mismatches and "Rendered fewer/more hooks than expected" errors.

## Common Violations {/*common-violations*/}

These patterns violate the Rules of Hooks:

- **Hooks in conditions** (`if`/`else`, ternary, `&&`/`||`)
- **Hooks in loops** (`for`, `while`, `do-while`)
- **Hooks after early returns**
- **Hooks in callbacks/event handlers**
- **Hooks in async functions**
- **Hooks in class methods**
- **Hooks at module level**

> **Note:**
>
> 
> 
> ### `use` hook {/*use-hook*/}
> 
> The `use` hook is different from other React hooks. You can call it conditionally and in loops:
> 
> ```js
> // ✅ `use` can be conditional
> if (shouldFetch) {
>   const data = use(fetchPromise);
> }
> 
> // ✅ `use` can be in loops
> for (const promise of promises) {
>   results.push(use(promise));
> }
> ```
> 
> However, `use` still has restrictions:
> - Can't be wrapped in try/catch
> - Must be called inside a component or hook
> 
> Learn more: [`use` API Reference](/reference/react/use)
> 
> 


### Invalid {/*invalid*/}

Examples of incorrect code for this rule:

```js
// ❌ Hook in condition
if (isLoggedIn) {
  const [user, setUser] = useState(null);
}

// ❌ Hook after early return
if (!data) return <Loading />;
const [processed, setProcessed] = useState(data);

// ❌ Hook in callback
<button onClick={() => {
  const [clicked, setClicked] = useState(false);
}}/>

// ❌ `use` in try/catch
try {
  const data = use(promise);
} catch (e) {
  // error handling
}

// ❌ Hook at module level
const globalState = useState(0); // Outside component
```

### Valid {/*valid*/}

Examples of correct code for this rule:

```js
function Component({ isSpecial, shouldFetch, fetchPromise }) {
  // ✅ Hooks at top level
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  if (!isSpecial) {
    return null;
  }

  if (shouldFetch) {
    // ✅ `use` can be conditional
    const data = use(fetchPromise);
    return <div>{data}</div>;
  }

  return <div>{name}: {count}</div>;
}
```

## Troubleshooting {/*troubleshooting*/}

### I want to fetch data based on some condition {/*conditional-data-fetching*/}

You're trying to conditionally call useEffect:

```js
// ❌ Conditional hook
if (isLoggedIn) {
  useEffect(() => {
    fetchUserData();
  }, []);
}
```

Call the hook unconditionally, check condition inside:

```js
// ✅ Condition inside hook
useEffect(() => {
  if (isLoggedIn) {
    fetchUserData();
  }
}, [isLoggedIn]);
```

> **Note:**
>
> 
> 
> There are better ways to fetch data rather than in a useEffect. Consider using TanStack Query, useSWR, or React Router 6.4+ for data fetching. These solutions handle deduplicating requests, caching responses, and avoiding network waterfalls.
> 
> Learn more: [Fetching Data](/learn/synchronizing-with-effects#fetching-data)
> 
> 


### I need different state for different scenarios {/*conditional-state-initialization*/}

You're trying to conditionally initialize state:

```js
// ❌ Conditional state
if (userType === 'admin') {
  const [permissions, setPermissions] = useState(adminPerms);
} else {
  const [permissions, setPermissions] = useState(userPerms);
}
```

Always call useState, conditionally set the initial value:

```js
// ✅ Conditional initial value
const [permissions, setPermissions] = useState(
  userType === 'admin' ? adminPerms : userPerms
);
```

## Options {/*options*/}

You can configure custom effect hooks using shared ESLint settings (available in `eslint-plugin-react-hooks` 6.1.1 and later):

```js
{
  "settings": {
    "react-hooks": {
      "additionalEffectHooks": "(useMyEffect|useCustomEffect)"
    }
  }
}
```

- `additionalEffectHooks`: Regex pattern matching custom hooks that should be treated as effects. This allows `useEffectEvent` and similar event functions to be called from your custom effect hooks.

This shared configuration is used by both `rules-of-hooks` and `exhaustive-deps` rules, ensuring consistent behavior across all hook-related linting.
