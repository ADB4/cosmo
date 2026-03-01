---
title: React Compiler
source: react.dev
syllabus_weeks: [5, 15]
topics: [React Compiler, automatic memoization, babel plugin, installation, configuration, directives, use memo, use no memo, debugging, incremental adoption]
---



# Introduction

React Compiler is a new build-time tool that automatically optimizes your React app. It works with plain JavaScript, and understands the [Rules of React](/reference/rules), so you don't need to rewrite any code to use it.

* What React Compiler does
* Getting started with the compiler
* Incremental adoption strategies
* Debugging and troubleshooting when things go wrong
* Using the compiler on your React library

## What does React Compiler do? {/*what-does-react-compiler-do*/}

React Compiler automatically optimizes your React application at build time. React is often fast enough without optimization, but sometimes you need to manually memoize components and values to keep your app responsive. This manual memoization is tedious, easy to get wrong, and adds extra code to maintain. React Compiler does this optimization automatically for you, freeing you from this mental burden so you can focus on building features.

### Before React Compiler {/*before-react-compiler*/}

Without the compiler, you need to manually memoize components and values to optimize re-renders:

```js
import { useMemo, useCallback, memo } from 'react';

const ExpensiveComponent = memo(function ExpensiveComponent({ data, onClick }) {
  const processedData = useMemo(() => {
    return expensiveProcessing(data);
  }, [data]);

  const handleClick = useCallback((item) => {
    onClick(item.id);
  }, [onClick]);

  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} onClick={() => handleClick(item)} />
      ))}
    </div>
  );
});
```


> **Note:**
>
> 
> 
> This manual memoization has a subtle bug that breaks memoization:
> 
> ```js [[2, 1, "() => handleClick(item)"]]
> <Item key={item.id} onClick={() => handleClick(item)} />
> ```
> 
> Even though `handleClick` is wrapped in `useCallback`, the arrow function `() => handleClick(item)` creates a new function every time the component renders. This means that `Item` will always receive a new `onClick` prop, breaking memoization.
> 
> React Compiler is able to optimize this correctly with or without the arrow function, ensuring that `Item` only re-renders when `props.onClick` changes.
> 
> 


### After React Compiler {/*after-react-compiler*/}

With React Compiler, you write the same code without manual memoization:

```js
function ExpensiveComponent({ data, onClick }) {
  const processedData = expensiveProcessing(data);

  const handleClick = (item) => {
    onClick(item.id);
  };

  return (
    <div>
      {processedData.map(item => (
        <Item key={item.id} onClick={() => handleClick(item)} />
      ))}
    </div>
  );
}
```

_[See this example in the React Compiler Playground](https://playground.react.dev/#N4Igzg9grgTgxgUxALhAMygOzgFwJYSYAEAogB4AOCmYeAbggMIQC2Fh1OAFMEQCYBDHAIA0RQowA2eOAGsiAXwCURYAB1iROITA4iFGBERgwCPgBEhAogF4iCStVoMACoeO1MAcy6DhSgG4NDSItHT0ACwFMPkkmaTlbIi48HAQWFRsAPlUQ0PFMKRlZFLSWADo8PkC8hSDMPJgEHFhiLjzQgB4+eiyO-OADIwQTM0thcpYBClL02xz2zXz8zoBJMqJZBABPG2BU9Mq+BQKiuT2uTJyomLizkoOMk4B6PqX8pSUFfs7nnro3qEapgFCAFEA)_

React Compiler automatically applies the optimal memoization, ensuring your app only re-renders when necessary.

> **Deep Dive: What kind of memoization does React Compiler add? {/*what-kind-of-memoization-does-react-compiler-add*/}**
>
> React Compiler's automatic memoization is primarily focused on **improving update performance** (re-rendering existing components), so it focuses on these two use cases:
> 
> 1. **Skipping cascading re-rendering of components**
>     * Re-rendering `<Parent />` causes many components in its component tree to re-render, even though only `<Parent />` has changed
> 1. **Skipping expensive calculations from outside of React**
>     * For example, calling `expensivelyProcessAReallyLargeArrayOfObjects()` inside of your component or hook that needs that data
> 
> #### Optimizing Re-renders {/*optimizing-re-renders*/}
> 
> React lets you express your UI as a function of their current state (more concretely: their props, state, and context). In its current implementation, when a component's state changes, React will re-render that component _and all of its children_ — unless you have applied some form of manual memoization with `useMemo()`, `useCallback()`, or `React.memo()`. For example, in the following example, `<MessageButton>` will re-render whenever `<FriendList>`'s state changes:
> 
> ```javascript
> function FriendList({ friends }) {
>   const onlineCount = useFriendOnlineCount();
>   if (friends.length === 0) {
>     return <NoFriends />;
>   }
>   return (
>     <div>
>       <span>{onlineCount} online</span>
>       {friends.map((friend) => (
>         <FriendListCard key={friend.id} friend={friend} />
>       ))}
>       <MessageButton />
>     </div>
>   );
> }
> ```
> [_See this example in the React Compiler Playground_](https://playground.react.dev/#N4Igzg9grgTgxgUxALhAMygOzgFwJYSYAEAYjHgpgCYAyeYOAFMEWuZVWEQL4CURwADrEicQgyKEANnkwIAwtEw4iAXiJQwCMhWoB5TDLmKsTXgG5hRInjRFGbXZwB0UygHMcACzWr1ABn4hEWsYBBxYYgAeADkIHQ4uAHoAPksRbisiMIiYYkYs6yiqPAA3FMLrIiiwAAcAQ0wU4GlZBSUcbklDNqikusaKkKrgR0TnAFt62sYHdmp+VRT7SqrqhOo6Bnl6mCoiAGsEAE9VUfmqZzwqLrHqM7ubolTVol5eTOGigFkEMDB6u4EAAhKA4HCEZ5DNZ9ErlLIWYTcEDcIA)
> 
> React Compiler automatically applies the equivalent of manual memoization, ensuring that only the relevant parts of an app re-render as state changes, which is sometimes referred to as "fine-grained reactivity". In the above example, React Compiler determines that the return value of `<FriendListCard />` can be reused even as `friends` changes, and can avoid recreating this JSX _and_ avoid re-rendering `<MessageButton>` as the count changes.
> 
> #### Expensive calculations also get memoized {/*expensive-calculations-also-get-memoized*/}
> 
> React Compiler can also automatically memoize expensive calculations used during rendering:
> 
> ```js
> // **Not** memoized by React Compiler, since this is not a component or hook
> function expensivelyProcessAReallyLargeArrayOfObjects() { /* ... */ }
> 
> // Memoized by React Compiler since this is a component
> function TableContainer({ items }) {
>   // This function call would be memoized:
>   const data = expensivelyProcessAReallyLargeArrayOfObjects(items);
>   // ...
> }
> ```
> [_See this example in the React Compiler Playground_](https://playground.react.dev/#N4Igzg9grgTgxgUxALhAejQAgFTYHIQAuumAtgqRAJYBeCAJpgEYCemASggIZyGYDCEUgAcqAGwQwANJjBUAdokyEAFlTCZ1meUUxdMcIcIjyE8vhBiYVECAGsAOvIBmURYSonMCAB7CzcgBuCGIsAAowEIhgYACCnFxioQAyXDAA5gixMDBcLADyzvlMAFYIvGAAFACUmMCYaNiYAHStOFgAvk5OGJgAshTUdIysHNy8AkbikrIKSqpaWvqGIiZmhE6u7p7ymAAqXEwSguZcCpKV9VSEFBodtcBOmAYmYHz0XIT6ALzefgFUYKhCJRBAxeLcJIsVIZLI5PKFYplCqVa63aoAbm6u0wMAQhFguwAPPRAQA+YAfL4dIloUmBMlODogDpAA)
> 
> However, if `expensivelyProcessAReallyLargeArrayOfObjects` is truly an expensive function, you may want to consider implementing its own memoization outside of React, because:
> 
> - React Compiler only memoizes React components and hooks, not every function
> - React Compiler's memoization is not shared across multiple components or hooks
> 
> So if `expensivelyProcessAReallyLargeArrayOfObjects` was used in many different components, even if the same exact items were passed down, that expensive calculation would be run repeatedly. We recommend [profiling](reference/react/useMemo#how-to-tell-if-a-calculation-is-expensive) first to see if it really is that expensive before making code more complicated.


## Should I try out the compiler? {/*should-i-try-out-the-compiler*/}

We encourage everyone to start using React Compiler. While the compiler is still an optional addition to React today, in the future some features may require the compiler in order to fully work.

### Is it safe to use? {/*is-it-safe-to-use*/}

React Compiler is now stable and has been tested extensively in production. While it has been used in production at companies like Meta, rolling out the compiler to production for your app will depend on the health of your codebase and how well you've followed the [Rules of React](/reference/rules).

## What build tools are supported? {/*what-build-tools-are-supported*/}

React Compiler can be installed across [several build tools](/learn/react-compiler/installation) such as Babel, Vite, Metro, and Rsbuild.

React Compiler is primarily a light Babel plugin wrapper around the core compiler, which was designed to be decoupled from Babel itself. While the initial stable version of the compiler will remain primarily a Babel plugin, we are working with the swc and [oxc](https://github.com/oxc-project/oxc/issues/10048) teams to build first class support for React Compiler so you won't have to add Babel back to your build pipelines in the future.

Next.js users can enable the swc-invoked React Compiler by using [v15.3.1](https://github.com/vercel/next.js/releases/tag/v15.3.1) and up.

## What should I do about useMemo, useCallback, and React.memo? {/*what-should-i-do-about-usememo-usecallback-and-reactmemo*/}

By default, React Compiler will memoize your code based on its analysis and heuristics. In most cases, this memoization will be as precise, or moreso, than what you may have written.

However, in some cases developers may need more control over memoization. The `useMemo` and `useCallback` hooks can continue to be used with React Compiler as an escape hatch to provide control over which values are memoized. A common use-case for this is if a memoized value is used as an effect dependency, in order to ensure that an effect does not fire repeatedly even when its dependencies do not meaningfully change.

For new code, we recommend relying on the compiler for memoization and using `useMemo`/`useCallback` where needed to achieve precise control.

For existing code, we recommend either leaving existing memoization in place (removing it can change compilation output) or carefully testing before removing the memoization.

## Try React Compiler {/*try-react-compiler*/}

This section will help you get started with React Compiler and understand how to use it effectively in your projects.

* **[Installation](/learn/react-compiler/installation)** - Install React Compiler and configure it for your build tools
* **[React Version Compatibility](/reference/react-compiler/target)** - Support for React 17, 18, and 19
* **[Configuration](/reference/react-compiler/configuration)** - Customize the compiler for your specific needs
* **[Incremental Adoption](/learn/react-compiler/incremental-adoption)** - Strategies for gradually rolling out the compiler in existing codebases
* **[Debugging and Troubleshooting](/learn/react-compiler/debugging)** - Identify and fix issues when using the compiler
* **[Compiling Libraries](/reference/react-compiler/compiling-libraries)** - Best practices for shipping compiled code
* **[API Reference](/reference/react-compiler/configuration)** - Detailed documentation of all configuration options

## Additional resources {/*additional-resources*/}

In addition to these docs, we recommend checking the [React Compiler Working Group](https://github.com/reactwg/react-compiler) for additional information and discussion about the compiler.



# Installation

This guide will help you install and configure React Compiler in your React application.

* How to install React Compiler
* Basic configuration for different build tools
* How to verify your setup is working

## Prerequisites {/*prerequisites*/}

React Compiler is designed to work best with React 19, but it also supports React 17 and 18. Learn more about [React version compatibility](/reference/react-compiler/target).

## Installation {/*installation*/}

Install React Compiler as a `devDependency`:

<TerminalBlock>
npm install -D babel-plugin-react-compiler@latest
</TerminalBlock>

Or with Yarn:

<TerminalBlock>
yarn add -D babel-plugin-react-compiler@latest
</TerminalBlock>

Or with pnpm:

<TerminalBlock>
pnpm install -D babel-plugin-react-compiler@latest
</TerminalBlock>

## Basic Setup {/*basic-setup*/}

React Compiler is designed to work by default without any configuration. However, if you need to configure it in special circumstances (for example, to target React versions below 19), refer to the [compiler options reference](/reference/react-compiler/configuration).

The setup process depends on your build tool. React Compiler includes a Babel plugin that integrates with your build pipeline.

> **Pitfall:**
>
> 
> React Compiler must run **first** in your Babel plugin pipeline. The compiler needs the original source information for proper analysis, so it must process your code before other transformations.
> 


### Babel {/*babel*/}

Create or update your `babel.config.js`:

```js {3}
module.exports = {
  plugins: [
    'babel-plugin-react-compiler', // must run first!
    // ... other plugins
  ],
  // ... other config
};
```

### Vite {/*vite*/}

If you use Vite, you can add the plugin to vite-plugin-react:

```js {3,9}
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: ['babel-plugin-react-compiler'],
      },
    }),
  ],
});
```

Alternatively, if you prefer a separate Babel plugin for Vite:

<TerminalBlock>
npm install -D vite-plugin-babel
</TerminalBlock>

```js {2,11}
// vite.config.js
import babel from 'vite-plugin-babel';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react(),
    babel({
      babelConfig: {
        plugins: ['babel-plugin-react-compiler'],
      },
    }),
  ],
});
```

### Next.js {/*usage-with-nextjs*/}

Please refer to the [Next.js docs](https://nextjs.org/docs/app/api-reference/next-config-js/reactCompiler) for more information.

### React Router {/*usage-with-react-router*/}
Install `vite-plugin-babel`, and add the compiler's Babel plugin to it:

<TerminalBlock>
npm install vite-plugin-babel
</TerminalBlock>

```js {3-4,16}
// vite.config.js
import { defineConfig } from "vite";
import babel from "vite-plugin-babel";
import { reactRouter } from "@react-router/dev/vite";

const ReactCompilerConfig = { /* ... */ };

export default defineConfig({
  plugins: [
    reactRouter(),
    babel({
      filter: /\.[jt]sx?$/,
      babelConfig: {
        presets: ["@babel/preset-typescript"], // if you use TypeScript
        plugins: [
          ["babel-plugin-react-compiler", ReactCompilerConfig],
        ],
      },
    }),
  ],
});
```

### Webpack {/*usage-with-webpack*/}

A community webpack loader is [now available here](https://github.com/SukkaW/react-compiler-webpack).

### Expo {/*usage-with-expo*/}

Please refer to [Expo's docs](https://docs.expo.dev/guides/react-compiler/) to enable and use the React Compiler in Expo apps.

### Metro (React Native) {/*usage-with-react-native-metro*/}

React Native uses Babel via Metro, so refer to the [Usage with Babel](#babel) section for installation instructions.

### Rspack {/*usage-with-rspack*/}

Please refer to [Rspack's docs](https://rspack.dev/guide/tech/react#react-compiler) to enable and use the React Compiler in Rspack apps.

### Rsbuild {/*usage-with-rsbuild*/}

Please refer to [Rsbuild's docs](https://rsbuild.dev/guide/framework/react#react-compiler) to enable and use the React Compiler in Rsbuild apps.


## ESLint Integration {/*eslint-integration*/}

React Compiler includes an ESLint rule that helps identify code that can't be optimized. When the ESLint rule reports an error, it means the compiler will skip optimizing that specific component or hook. This is safe: the compiler will continue optimizing other parts of your codebase. You don't need to fix all violations immediately. Address them at your own pace to gradually increase the number of optimized components.

Install the ESLint plugin:

<TerminalBlock>
npm install -D eslint-plugin-react-hooks@latest
</TerminalBlock>

If you haven't already configured eslint-plugin-react-hooks, follow the [installation instructions in the readme](https://github.com/facebook/react/blob/main/packages/eslint-plugin-react-hooks/README.md#installation). The compiler rules are available in the `recommended-latest` preset.

The ESLint rule will:
- Identify violations of the [Rules of React](/reference/rules)
- Show which components can't be optimized
- Provide helpful error messages for fixing issues

## Verify Your Setup {/*verify-your-setup*/}

After installation, verify that React Compiler is working correctly.

### Check React DevTools {/*check-react-devtools*/}

Components optimized by React Compiler will show a "Memo ✨" badge in React DevTools:

1. Install the [React Developer Tools](/learn/react-developer-tools) browser extension
2. Open your app in development mode
3. Open React DevTools
4. Look for the ✨ emoji next to component names

If the compiler is working:
- Components will show a "Memo ✨" badge in React DevTools
- Expensive calculations will be automatically memoized
- No manual `useMemo` is required

### Check Build Output {/*check-build-output*/}

You can also verify the compiler is running by checking your build output. The compiled code will include automatic memoization logic that the compiler adds automatically.

```js
import { c as _c } from "react/compiler-runtime";
export default function MyApp() {
  const $ = _c(1);
  let t0;
  if ($[0] === Symbol.for("react.memo_cache_sentinel")) {
    t0 = <div>Hello World</div>;
    $[0] = t0;
  } else {
    t0 = $[0];
  }
  return t0;
}

```

## Troubleshooting {/*troubleshooting*/}

### Opting out specific components {/*opting-out-specific-components*/}

If a component is causing issues after compilation, you can temporarily opt it out using the `"use no memo"` directive:

```js
function ProblematicComponent() {
  "use no memo";
  // Component code here
}
```

This tells the compiler to skip optimization for this specific component. You should fix the underlying issue and remove the directive once resolved.

For more troubleshooting help, see the [debugging guide](/learn/react-compiler/debugging).

## Next Steps {/*next-steps*/}

Now that you have React Compiler installed, learn more about:

- [React version compatibility](/reference/react-compiler/target) for React 17 and 18
- [Configuration options](/reference/react-compiler/configuration) to customize the compiler
- [Incremental adoption strategies](/learn/react-compiler/incremental-adoption) for existing codebases
- [Debugging techniques](/learn/react-compiler/debugging) for troubleshooting issues
- [Compiling Libraries guide](/reference/react-compiler/compiling-libraries) for compiling your React library


# Debugging

This guide helps you identify and fix issues when using React Compiler. Learn how to debug compilation problems and resolve common issues.

* The difference between compiler errors and runtime issues
* Common patterns that break compilation
* Step-by-step debugging workflow

## Understanding Compiler Behavior {/*understanding-compiler-behavior*/}

React Compiler is designed to handle code that follows the [Rules of React](/reference/rules). When it encounters code that might break these rules, it safely skips optimization rather than risk changing your app's behavior.

### Compiler Errors vs Runtime Issues {/*compiler-errors-vs-runtime-issues*/}

**Compiler errors** occur at build time and prevent your code from compiling. These are rare because the compiler is designed to skip problematic code rather than fail.

**Runtime issues** occur when compiled code behaves differently than expected. Most of the time, if you encounter an issue with React Compiler, it's a runtime issue. This typically happens when your code violates the Rules of React in subtle ways that the compiler couldn't detect, and the compiler mistakenly compiled a component it should have skipped.

When debugging runtime issues, focus your efforts on finding Rules of React violations in the affected components that were not detected by the ESLint rule. The compiler relies on your code following these rules, and when they're broken in ways it can't detect, that's when runtime problems occur.


## Common Breaking Patterns {/*common-breaking-patterns*/}

One of the main ways React Compiler can break your app is if your code was written to rely on memoization for correctness. This means your app depends on specific values being memoized to work properly. Since the compiler may memoize differently than your manual approach, this can lead to unexpected behavior like effects over-firing, infinite loops, or missing updates.

Common scenarios where this occurs:

- **Effects that rely on referential equality** - When effects depend on objects or arrays maintaining the same reference across renders
- **Dependency arrays that need stable references** - When unstable dependencies cause effects to fire too often or create infinite loops
- **Conditional logic based on reference checks** - When code uses referential equality checks for caching or optimization

## Debugging Workflow {/*debugging-workflow*/}

Follow these steps when you encounter issues:

### Compiler Build Errors {/*compiler-build-errors*/}

If you encounter a compiler error that unexpectedly breaks your build, this is likely a bug in the compiler. Report it to the [facebook/react](https://github.com/facebook/react/issues) repository with:
- The error message
- The code that caused the error
- Your React and compiler versions

### Runtime Issues {/*runtime-issues*/}

For runtime behavior issues:

### 1. Temporarily Disable Compilation {/*temporarily-disable-compilation*/}

Use `"use no memo"` to isolate whether an issue is compiler-related:

```js
function ProblematicComponent() {
  "use no memo"; // Skip compilation for this component
  // ... rest of component
}
```

If the issue disappears, it's likely related to a Rules of React violation.

You can also try removing manual memoization (useMemo, useCallback, memo) from the problematic component to verify that your app works correctly without any memoization. If the bug still occurs when all memoization is removed, you have a Rules of React violation that needs to be fixed.

### 2. Fix Issues Step by Step {/*fix-issues-step-by-step*/}

1. Identify the root cause (often memoization-for-correctness)
2. Test after each fix
3. Remove `"use no memo"` once fixed
4. Verify the component shows the ✨ badge in React DevTools

## Reporting Compiler Bugs {/*reporting-compiler-bugs*/}

If you believe you've found a compiler bug:

1. **Verify it's not a Rules of React violation** - Check with ESLint
2. **Create a minimal reproduction** - Isolate the issue in a small example
3. **Test without the compiler** - Confirm the issue only occurs with compilation
4. **File an [issue](https://github.com/facebook/react/issues/new?template=compiler_bug_report.yml)**:
   - React and compiler versions
   - Minimal reproduction code
   - Expected vs actual behavior
   - Any error messages

## Next Steps {/*next-steps*/}

- Review the [Rules of React](/reference/rules) to prevent issues
- Check the [incremental adoption guide](/learn/react-compiler/incremental-adoption) for gradual rollout strategies

# Incremental Adoption

React Compiler can be adopted incrementally, allowing you to try it on specific parts of your codebase first. This guide shows you how to gradually roll out the compiler in existing projects.

* Why incremental adoption is recommended
* Using Babel overrides for directory-based adoption
* Using the "use memo" directive for opt-in compilation
* Using the "use no memo" directive to exclude components
* Runtime feature flags with gating
* Monitoring your adoption progress

## Why Incremental Adoption? {/*why-incremental-adoption*/}

React Compiler is designed to optimize your entire codebase automatically, but you don't have to adopt it all at once. Incremental adoption gives you control over the rollout process, letting you test the compiler on small parts of your app before expanding to the rest.

Starting small helps you build confidence in the compiler's optimizations. You can verify that your app behaves correctly with compiled code, measure performance improvements, and identify any edge cases specific to your codebase. This approach is especially valuable for production applications where stability is critical.

Incremental adoption also makes it easier to address any Rules of React violations the compiler might find. Instead of fixing violations across your entire codebase at once, you can tackle them systematically as you expand compiler coverage. This keeps the migration manageable and reduces the risk of introducing bugs.

By controlling which parts of your code get compiled, you can also run A/B tests to measure the real-world impact of the compiler's optimizations. This data helps you make informed decisions about full adoption and demonstrates the value to your team.

## Approaches to Incremental Adoption {/*approaches-to-incremental-adoption*/}

There are three main approaches to adopt React Compiler incrementally:

1. **Babel overrides** - Apply the compiler to specific directories
2. **Opt-in with "use memo"** - Only compile components that explicitly opt in
3. **Runtime gating** - Control compilation with feature flags

All approaches allow you to test the compiler on specific parts of your application before full rollout.

## Directory-Based Adoption with Babel Overrides {/*directory-based-adoption*/}

Babel's `overrides` option lets you apply different plugins to different parts of your codebase. This is ideal for gradually adopting React Compiler directory by directory.

### Basic Configuration {/*basic-configuration*/}

Start by applying the compiler to a specific directory:

```js
// babel.config.js
module.exports = {
  plugins: [
    // Global plugins that apply to all files
  ],
  overrides: [
    {
      test: './src/modern/**/*.{js,jsx,ts,tsx}',
      plugins: [
        'babel-plugin-react-compiler'
      ]
    }
  ]
};
```

### Expanding Coverage {/*expanding-coverage*/}

As you gain confidence, add more directories:

```js
// babel.config.js
module.exports = {
  plugins: [
    // Global plugins
  ],
  overrides: [
    {
      test: ['./src/modern/**/*.{js,jsx,ts,tsx}', './src/features/**/*.{js,jsx,ts,tsx}'],
      plugins: [
        'babel-plugin-react-compiler'
      ]
    },
    {
      test: './src/legacy/**/*.{js,jsx,ts,tsx}',
      plugins: [
        // Different plugins for legacy code
      ]
    }
  ]
};
```

### With Compiler Options {/*with-compiler-options*/}

You can also configure compiler options per override:

```js
// babel.config.js
module.exports = {
  plugins: [],
  overrides: [
    {
      test: './src/experimental/**/*.{js,jsx,ts,tsx}',
      plugins: [
        ['babel-plugin-react-compiler', {
          // options ...
        }]
      ]
    },
    {
      test: './src/production/**/*.{js,jsx,ts,tsx}',
      plugins: [
        ['babel-plugin-react-compiler', {
          // options ...
        }]
      ]
    }
  ]
};
```


## Opt-in Mode with "use memo" {/*opt-in-mode-with-use-memo*/}

For maximum control, you can use `compilationMode: 'annotation'` to only compile components and hooks that explicitly opt in with the `"use memo"` directive.

> **Note:**
>
> 
> This approach gives you fine-grained control over individual components and hooks. It's useful when you want to test the compiler on specific components without affecting entire directories.
> 


### Annotation Mode Configuration {/*annotation-mode-configuration*/}

```js
// babel.config.js
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      compilationMode: 'annotation',
    }],
  ],
};
```

### Using the Directive {/*using-the-directive*/}

Add `"use memo"` at the beginning of functions you want to compile:

```js
function TodoList({ todos }) {
  "use memo"; // Opt this component into compilation

  const sortedTodos = todos.slice().sort();

  return (
    <ul>
      {sortedTodos.map(todo => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </ul>
  );
}

function useSortedData(data) {
  "use memo"; // Opt this hook into compilation

  return data.slice().sort();
}
```

With `compilationMode: 'annotation'`, you must:
- Add `"use memo"` to every component you want optimized
- Add `"use memo"` to every custom hook
- Remember to add it to new components

This gives you precise control over which components are compiled while you evaluate the compiler's impact.

## Runtime Feature Flags with Gating {/*runtime-feature-flags-with-gating*/}

The `gating` option enables you to control compilation at runtime using feature flags. This is useful for running A/B tests or gradually rolling out the compiler based on user segments.

### How Gating Works {/*how-gating-works*/}

The compiler wraps optimized code in a runtime check. If the gate returns `true`, the optimized version runs. Otherwise, the original code runs.

### Gating Configuration {/*gating-configuration*/}

```js
// babel.config.js
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      gating: {
        source: 'ReactCompilerFeatureFlags',
        importSpecifierName: 'isCompilerEnabled',
      },
    }],
  ],
};
```

### Implementing the Feature Flag {/*implementing-the-feature-flag*/}

Create a module that exports your gating function:

```js
// ReactCompilerFeatureFlags.js
export function isCompilerEnabled() {
  // Use your feature flag system
  return getFeatureFlag('react-compiler-enabled');
}
```

## Troubleshooting Adoption {/*troubleshooting-adoption*/}

If you encounter issues during adoption:

1. Use `"use no memo"` to temporarily exclude problematic components
2. Check the [debugging guide](/learn/react-compiler/debugging) for common issues
3. Fix Rules of React violations identified by the ESLint plugin
4. Consider using `compilationMode: 'annotation'` for more gradual adoption

## Next Steps {/*next-steps*/}

- Read the [configuration guide](/reference/react-compiler/configuration) for more options
- Learn about [debugging techniques](/learn/react-compiler/debugging)
- Check the [API reference](/reference/react-compiler/configuration) for all compiler options

# Index

## Introduction {/*introduction*/}

Learn [what React Compiler does](/learn/react-compiler/introduction) and how it automatically optimizes your React application by handling memoization for you, eliminating the need for manual `useMemo`, `useCallback`, and `React.memo`.

## Installation {/*installation*/}

Get started with [installing React Compiler](/learn/react-compiler/installation) and learn how to configure it with your build tools.


## Incremental Adoption {/*incremental-adoption*/}

Learn [strategies for gradually adopting React Compiler](/learn/react-compiler/incremental-adoption) in your existing codebase if you're not ready to enable it everywhere yet.

## Debugging and Troubleshooting {/*debugging-and-troubleshooting*/}

When things don't work as expected, use our [debugging guide](/learn/react-compiler/debugging) to understand the difference between compiler errors and runtime issues, identify common breaking patterns, and follow a systematic debugging workflow.

## Configuration and Reference {/*configuration-and-reference*/}

For detailed configuration options and API reference:

- [Configuration Options](/reference/react-compiler/configuration) - All compiler configuration options including React version compatibility
- [Directives](/reference/react-compiler/directives) - Function-level compilation control
- [Compiling Libraries](/reference/react-compiler/compiling-libraries) - Shipping pre-compiled libraries

## Additional resources {/*additional-resources*/}

In addition to these docs, we recommend checking the [React Compiler Working Group](https://github.com/reactwg/react-compiler) for additional information and discussion about the compiler.



# Configuration

This page lists all configuration options available in React Compiler.

> **Note:**
>
> 
> 
> For most apps, the default options should work out of the box. If you have a special need, you can use these advanced options.
> 
> 


```js
// babel.config.js
module.exports = {
  plugins: [
    [
      'babel-plugin-react-compiler', {
        // compiler options
      }
    ]
  ]
};
```

---

## Compilation Control {/*compilation-control*/}

These options control *what* the compiler optimizes and *how* it selects components and hooks to compile.

* [`compilationMode`](/reference/react-compiler/compilationMode) controls the strategy for selecting functions to compile (e.g., all functions, only annotated ones, or intelligent detection).

```js
{
  compilationMode: 'annotation' // Only compile "use memo" functions
}
```

---

## Version Compatibility {/*version-compatibility*/}

React version configuration ensures the compiler generates code compatible with your React version.

[`target`](/reference/react-compiler/target) specifies which React version you're using (17, 18, or 19).

```js
// For React 18 projects
{
  target: '18' // Also requires react-compiler-runtime package
}
```

---

## Error Handling {/*error-handling*/}

These options control how the compiler responds to code that doesn't follow the [Rules of React](/reference/rules).

[`panicThreshold`](/reference/react-compiler/panicThreshold) determines whether to fail the build or skip problematic components.

```js
// Recommended for production
{
  panicThreshold: 'none' // Skip components with errors instead of failing the build
}
```

---

## Debugging {/*debugging*/}

Logging and analysis options help you understand what the compiler is doing.

[`logger`](/reference/react-compiler/logger) provides custom logging for compilation events.

```js
{
  logger: {
    logEvent(filename, event) {
      if (event.kind === 'CompileSuccess') {
        console.log('Compiled:', filename);
      }
    }
  }
}
```

---

## Feature Flags {/*feature-flags*/}

Conditional compilation lets you control when optimized code is used.

[`gating`](/reference/react-compiler/gating) enables runtime feature flags for A/B testing or gradual rollouts.

```js
{
  gating: {
    source: 'my-feature-flags',
    importSpecifierName: 'isCompilerEnabled'
  }
}
```

---

## Common Configuration Patterns {/*common-patterns*/}

### Default configuration {/*default-configuration*/}

For most React 19 applications, the compiler works without configuration:

```js
// babel.config.js
module.exports = {
  plugins: [
    'babel-plugin-react-compiler'
  ]
};
```

### React 17/18 projects {/*react-17-18*/}

Older React versions need the runtime package and target configuration:

```bash
npm install react-compiler-runtime@latest
```

```js
{
  target: '18' // or '17'
}
```

### Incremental adoption {/*incremental-adoption*/}

Start with specific directories and expand gradually:

```js
{
  compilationMode: 'annotation' // Only compile "use memo" functions
}
```



# Compilationmode

The `compilationMode` option controls how the React Compiler selects which functions to compile.

```js
{
  compilationMode: 'infer' // or 'annotation', 'syntax', 'all'
}
```

<InlineToc />

---

## Reference {/*reference*/}

### `compilationMode` {/*compilationmode*/}

Controls the strategy for determining which functions the React Compiler will optimize.

#### Type {/*type*/}

```
'infer' | 'syntax' | 'annotation' | 'all'
```

#### Default value {/*default-value*/}

`'infer'`

#### Options {/*options*/}

- **`'infer'`** (default): The compiler uses intelligent heuristics to identify React components and hooks:
  - Functions explicitly annotated with `"use memo"` directive
  - Functions that are named like components (PascalCase) or hooks (`use` prefix) AND create JSX and/or call other hooks

- **`'annotation'`**: Only compile functions explicitly marked with the `"use memo"` directive. Ideal for incremental adoption.

- **`'syntax'`**: Only compile components and hooks that use Flow's [component](https://flow.org/en/docs/react/component-syntax/) and [hook](https://flow.org/en/docs/react/hook-syntax/) syntax.

- **`'all'`**: Compile all top-level functions. Not recommended as it may compile non-React functions.

#### Caveats {/*caveats*/}

- The `'infer'` mode requires functions to follow React naming conventions to be detected
- Using `'all'` mode may negatively impact performance by compiling utility functions
- The `'syntax'` mode requires Flow and won't work with TypeScript
- Regardless of mode, functions with `"use no memo"` directive are always skipped

---

## Usage {/*usage*/}

### Default inference mode {/*default-inference-mode*/}

The default `'infer'` mode works well for most codebases that follow React conventions:

```js
{
  compilationMode: 'infer'
}
```

With this mode, these functions will be compiled:

```js
// ✅ Compiled: Named like a component + returns JSX
function Button(props) {
  return <button>{props.label}</button>;
}

// ✅ Compiled: Named like a hook + calls hooks
function useCounter() {
  const [count, setCount] = useState(0);
  return [count, setCount];
}

// ✅ Compiled: Explicit directive
function expensiveCalculation(data) {
  "use memo";
  return data.reduce(/* ... */);
}

// ❌ Not compiled: Not a component/hook pattern
function calculateTotal(items) {
  return items.reduce((a, b) => a + b, 0);
}
```

### Incremental adoption with annotation mode {/*incremental-adoption*/}

For gradual migration, use `'annotation'` mode to only compile marked functions:

```js
{
  compilationMode: 'annotation'
}
```

Then explicitly mark functions to compile:

```js
// Only this function will be compiled
function ExpensiveList(props) {
  "use memo";
  return (
    <ul>
      {props.items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}

// This won't be compiled without the directive
function NormalComponent(props) {
  return <div>{props.content}</div>;
}
```

### Using Flow syntax mode {/*flow-syntax-mode*/}

If your codebase uses Flow instead of TypeScript:

```js
{
  compilationMode: 'syntax'
}
```

Then use Flow's component syntax:

```js
// Compiled: Flow component syntax
component Button(label: string) {
  return <button>{label}</button>;
}

// Compiled: Flow hook syntax
hook useCounter(initial: number) {
  const [count, setCount] = useState(initial);
  return [count, setCount];
}

// Not compiled: Regular function syntax
function helper(data) {
  return process(data);
}
```

### Opting out specific functions {/*opting-out*/}

Regardless of compilation mode, use `"use no memo"` to skip compilation:

```js
function ComponentWithSideEffects() {
  "use no memo"; // Prevent compilation

  // This component has side effects that shouldn't be memoized
  logToAnalytics('component_rendered');

  return <div>Content</div>;
}
```

---

## Troubleshooting {/*troubleshooting*/}

### Component not being compiled in infer mode {/*component-not-compiled-infer*/}

In `'infer'` mode, ensure your component follows React conventions:

```js
// ❌ Won't be compiled: lowercase name
function button(props) {
  return <button>{props.label}</button>;
}

// ✅ Will be compiled: PascalCase name
function Button(props) {
  return <button>{props.label}</button>;
}

// ❌ Won't be compiled: doesn't create JSX or call hooks
function useData() {
  return window.localStorage.getItem('data');
}

// ✅ Will be compiled: calls a hook
function useData() {
  const [data] = useState(() => window.localStorage.getItem('data'));
  return data;
}
```


# Compiling Libraries

This guide helps library authors understand how to use React Compiler to ship optimized library code to their users.

<InlineToc />

## Why Ship Compiled Code? {/*why-ship-compiled-code*/}

As a library author, you can compile your library code before publishing to npm. This provides several benefits:

- **Performance improvements for all users** - Your library users get optimized code even if they aren't using React Compiler yet
- **No configuration required by users** - The optimizations work out of the box
- **Consistent behavior** - All users get the same optimized version regardless of their build setup

## Setting Up Compilation {/*setting-up-compilation*/}

Add React Compiler to your library's build process:

<TerminalBlock>
npm install -D babel-plugin-react-compiler@latest
</TerminalBlock>

Configure your build tool to compile your library. For example, with Babel:

```js
// babel.config.js
module.exports = {
  plugins: [
    'babel-plugin-react-compiler',
  ],
  // ... other config
};
```

## Backwards Compatibility {/*backwards-compatibility*/}

If your library supports React versions below 19, you'll need additional configuration:

### 1. Install the runtime package {/*install-runtime-package*/}

We recommend installing react-compiler-runtime as a direct dependency:

<TerminalBlock>
npm install react-compiler-runtime@latest
</TerminalBlock>

```json
{
  "dependencies": {
    "react-compiler-runtime": "^1.0.0"
  },
  "peerDependencies": {
    "react": "^17.0.0 || ^18.0.0 || ^19.0.0"
  }
}
```

### 2. Configure the target version {/*configure-target-version*/}

Set the minimum React version your library supports:

```js
{
  target: '17', // Minimum supported React version
}
```

## Testing Strategy {/*testing-strategy*/}

Test your library both with and without compilation to ensure compatibility. Run your existing test suite against the compiled code, and also create a separate test configuration that bypasses the compiler. This helps catch any issues that might arise from the compilation process and ensures your library works correctly in all scenarios.

## Troubleshooting {/*troubleshooting*/}

### Library doesn't work with older React versions {/*library-doesnt-work-with-older-react-versions*/}

If your compiled library throws errors in React 17 or 18:

1. Verify you've installed `react-compiler-runtime` as a dependency
2. Check that your `target` configuration matches your minimum supported React version
3. Ensure the runtime package is included in your published bundle

### Compilation conflicts with other Babel plugins {/*compilation-conflicts-with-other-babel-plugins*/}

Some Babel plugins may conflict with React Compiler:

1. Place `babel-plugin-react-compiler` early in your plugin list
2. Disable conflicting optimizations in other plugins
3. Test your build output thoroughly

### Runtime module not found {/*runtime-module-not-found*/}

If users see "Cannot find module 'react-compiler-runtime'":

1. Ensure the runtime is listed in `dependencies`, not `devDependencies`
2. Check that your bundler includes the runtime in the output
3. Verify the package is published to npm with your library

## Next Steps {/*next-steps*/}

- Learn about [debugging techniques](/learn/react-compiler/debugging) for compiled code
- Check the [configuration options](/reference/react-compiler/configuration) for all compiler options
- Explore [compilation modes](/reference/react-compiler/compilationMode) for selective optimization

# Directives

React Compiler directives are special string literals that control whether specific functions are compiled.

```js
function MyComponent() {
  "use memo"; // Opt this component into compilation
  return <div>{/* ... */}</div>;
}
```

<InlineToc />

---

## Overview {/*overview*/}

React Compiler directives provide fine-grained control over which functions are optimized by the compiler. They are string literals placed at the beginning of a function body or at the top of a module.

### Available directives {/*available-directives*/}

* **[`"use memo"`](/reference/react-compiler/directives/use-memo)** - Opts a function into compilation
* **[`"use no memo"`](/reference/react-compiler/directives/use-no-memo)** - Opts a function out of compilation

### Quick comparison {/*quick-comparison*/}

| Directive | Purpose | When to use |
|-----------|---------|-------------|
| [`"use memo"`](/reference/react-compiler/directives/use-memo) | Force compilation | When using `annotation` mode or to override `infer` mode heuristics |
| [`"use no memo"`](/reference/react-compiler/directives/use-no-memo) | Prevent compilation | Debugging issues or working with incompatible code |

---

## Usage {/*usage*/}

### Function-level directives {/*function-level*/}

Place directives at the beginning of a function to control its compilation:

```js
// Opt into compilation
function OptimizedComponent() {
  "use memo";
  return <div>This will be optimized</div>;
}

// Opt out of compilation
function UnoptimizedComponent() {
  "use no memo";
  return <div>This won't be optimized</div>;
}
```

### Module-level directives {/*module-level*/}

Place directives at the top of a file to affect all functions in that module:

```js
// At the very top of the file
"use memo";

// All functions in this file will be compiled
function Component1() {
  return <div>Compiled</div>;
}

function Component2() {
  return <div>Also compiled</div>;
}

// Can be overridden at function level
function Component3() {
  "use no memo"; // This overrides the module directive
  return <div>Not compiled</div>;
}
```

### Compilation modes interaction {/*compilation-modes*/}

Directives behave differently depending on your [`compilationMode`](/reference/react-compiler/compilationMode):

* **`annotation` mode**: Only functions with `"use memo"` are compiled
* **`infer` mode**: Compiler decides what to compile, directives override decisions
* **`all` mode**: Everything is compiled, `"use no memo"` can exclude specific functions

---

## Best practices {/*best-practices*/}

### Use directives sparingly {/*use-sparingly*/}

Directives are escape hatches. Prefer configuring the compiler at the project level:

```js
// ✅ Good - project-wide configuration
{
  plugins: [
    ['babel-plugin-react-compiler', {
      compilationMode: 'infer'
    }]
  ]
}

// ⚠️ Use directives only when needed
function SpecialCase() {
  "use no memo"; // Document why this is needed
  // ...
}
```

### Document directive usage {/*document-usage*/}

Always explain why a directive is used:

```js
// ✅ Good - clear explanation
function DataGrid() {
  "use no memo"; // TODO: Remove after fixing issue with dynamic row heights (JIRA-123)
  // Complex grid implementation
}

// ❌ Bad - no explanation
function Mystery() {
  "use no memo";
  // ...
}
```

### Plan for removal {/*plan-removal*/}

Opt-out directives should be temporary:

1. Add the directive with a TODO comment
2. Create a tracking issue
3. Fix the underlying problem
4. Remove the directive

```js
function TemporaryWorkaround() {
  "use no memo"; // TODO: Remove after upgrading ThirdPartyLib to v2.0
  return <ThirdPartyComponent />;
}
```

---

## Common patterns {/*common-patterns*/}

### Gradual adoption {/*gradual-adoption*/}

When adopting the React Compiler in a large codebase:

```js
// Start with annotation mode
{
  compilationMode: 'annotation'
}

// Opt in stable components
function StableComponent() {
  "use memo";
  // Well-tested component
}

// Later, switch to infer mode and opt out problematic ones
function ProblematicComponent() {
  "use no memo"; // Fix issues before removing
  // ...
}
```


---

## Troubleshooting {/*troubleshooting*/}

For specific issues with directives, see the troubleshooting sections in:

* [`"use memo"` troubleshooting](/reference/react-compiler/directives/use-memo#troubleshooting)
* [`"use no memo"` troubleshooting](/reference/react-compiler/directives/use-no-memo#troubleshooting)

### Common issues {/*common-issues*/}

1. **Directive ignored**: Check placement (must be first) and spelling
2. **Compilation still happens**: Check `ignoreUseNoForget` setting
3. **Module directive not working**: Ensure it's before all imports

---

## See also {/*see-also*/}

* [`compilationMode`](/reference/react-compiler/compilationMode) - Configure how the compiler chooses what to optimize
* [`Configuration`](/reference/react-compiler/configuration) - Full compiler configuration options
* [React Compiler documentation](https://react.dev/learn/react-compiler) - Getting started guide

# Use Memo

`"use memo"` marks a function for React Compiler optimization.

> **Note:**
>
> 
> 
> In most cases, you don't need `"use memo"`. It's primarily needed in `annotation` mode where you must explicitly mark functions for optimization. In `infer` mode, the compiler automatically detects components and hooks by their naming patterns (PascalCase for components, `use` prefix for hooks). If a component or hook isn't being compiled in `infer` mode, you should fix its naming convention rather than forcing compilation with `"use memo"`.
> 
> 


<InlineToc />

---

## Reference {/*reference*/}

### `"use memo"` {/*use-memo*/}

Add `"use memo"` at the beginning of a function to mark it for React Compiler optimization.

```js {1}
function MyComponent() {
  "use memo";
  // ...
}
```

When a function contains `"use memo"`, the React Compiler will analyze and optimize it during build time. The compiler will automatically memoize values and components to prevent unnecessary re-computations and re-renders.

#### Caveats {/*caveats*/}

* `"use memo"` must be at the very beginning of a function body, before any imports or other code (comments are OK).
* The directive must be written with double or single quotes, not backticks.
* The directive must exactly match `"use memo"`.
* Only the first directive in a function is processed; additional directives are ignored.
* The effect of the directive depends on your [`compilationMode`](/reference/react-compiler/compilationMode) setting.

### How `"use memo"` marks functions for optimization {/*how-use-memo-marks*/}

In a React app that uses the React Compiler, functions are analyzed at build time to determine if they can be optimized. By default, the compiler automatically infers which components to memoize, but this can depend on your [`compilationMode`](/reference/react-compiler/compilationMode) setting if you've set it.

`"use memo"` explicitly marks a function for optimization, overriding the default behavior:

* In `annotation` mode: Only functions with `"use memo"` are optimized
* In `infer` mode: The compiler uses heuristics, but `"use memo"` forces optimization
* In `all` mode: Everything is optimized by default, making `"use memo"` redundant

The directive creates a clear boundary in your codebase between optimized and non-optimized code, giving you fine-grained control over the compilation process.

### When to use `"use memo"` {/*when-to-use*/}

You should consider using `"use memo"` when:

#### You're using annotation mode {/*annotation-mode-use*/}
In `compilationMode: 'annotation'`, the directive is required for any function you want optimized:

```js
// ✅ This component will be optimized
function OptimizedList() {
  "use memo";
  // ...
}

// ❌ This component won't be optimized
function SimpleWrapper() {
  // ...
}
```

#### You're gradually adopting React Compiler {/*gradual-adoption*/}
Start with `annotation` mode and selectively optimize stable components:

```js
// Start by optimizing leaf components
function Button({ onClick, children }) {
  "use memo";
  // ...
}

// Gradually move up the tree as you verify behavior
function ButtonGroup({ buttons }) {
  "use memo";
  // ...
}
```

---

## Usage {/*usage*/}

### Working with different compilation modes {/*compilation-modes*/}

The behavior of `"use memo"` changes based on your compiler configuration:

```js
// babel.config.js
module.exports = {
  plugins: [
    ['babel-plugin-react-compiler', {
      compilationMode: 'annotation' // or 'infer' or 'all'
    }]
  ]
};
```

#### Annotation mode {/*annotation-mode-example*/}
```js
// ✅ Optimized with "use memo"
function ProductCard({ product }) {
  "use memo";
  // ...
}

// ❌ Not optimized (no directive)
function ProductList({ products }) {
  // ...
}
```

#### Infer mode (default) {/*infer-mode-example*/}
```js
// Automatically memoized because this is named like a Component
function ComplexDashboard({ data }) {
  // ...
}

// Skipped: Is not named like a Component
function simpleDisplay({ text }) {
  // ...
}
```

In `infer` mode, the compiler automatically detects components and hooks by their naming patterns (PascalCase for components, `use` prefix for hooks). If a component or hook isn't being compiled in `infer` mode, you should fix its naming convention rather than forcing compilation with `"use memo"`.

---

## Troubleshooting {/*troubleshooting*/}

### Verifying optimization {/*verifying-optimization*/}

To confirm your component is being optimized:

1. Check the compiled output in your build
2. Use React DevTools to check for Memo ✨ badge

### See also {/*see-also*/}

* [`"use no memo"`](/reference/react-compiler/directives/use-no-memo) - Opt out of compilation
* [`compilationMode`](/reference/react-compiler/compilationMode) - Configure compilation behavior
* [React Compiler](/learn/react-compiler) - Getting started guide

# Use No Memo

`"use no memo"` prevents a function from being optimized by React Compiler.

<InlineToc />

---

## Reference {/*reference*/}

### `"use no memo"` {/*use-no-memo*/}

Add `"use no memo"` at the beginning of a function to prevent React Compiler optimization.

```js {1}
function MyComponent() {
  "use no memo";
  // ...
}
```

When a function contains `"use no memo"`, the React Compiler will skip it entirely during optimization. This is useful as a temporary escape hatch when debugging or when dealing with code that doesn't work correctly with the compiler.

#### Caveats {/*caveats*/}

* `"use no memo"` must be at the very beginning of a function body, before any imports or other code (comments are OK).
* The directive must be written with double or single quotes, not backticks.
* The directive must exactly match `"use no memo"` or its alias `"use no forget"`.
* This directive takes precedence over all compilation modes and other directives.
* It's intended as a temporary debugging tool, not a permanent solution.

### How `"use no memo"` opts-out of optimization {/*how-use-no-memo-opts-out*/}

React Compiler analyzes your code at build time to apply optimizations. `"use no memo"` creates an explicit boundary that tells the compiler to skip a function entirely.

This directive takes precedence over all other settings:
* In `all` mode: The function is skipped despite the global setting
* In `infer` mode: The function is skipped even if heuristics would optimize it

The compiler treats these functions as if the React Compiler wasn't enabled, leaving them exactly as written.

### When to use `"use no memo"` {/*when-to-use*/}

`"use no memo"` should be used sparingly and temporarily. Common scenarios include:

#### Debugging compiler issues {/*debugging-compiler*/}
When you suspect the compiler is causing issues, temporarily disable optimization to isolate the problem:

```js
function ProblematicComponent({ data }) {
  "use no memo"; // TODO: Remove after fixing issue #123

  // Rules of React violations that weren't statically detected
  // ...
}
```

#### Third-party library integration {/*third-party*/}
When integrating with libraries that might not be compatible with the compiler:

```js
function ThirdPartyWrapper() {
  "use no memo";

  useThirdPartyHook(); // Has side effects that compiler might optimize incorrectly
  // ...
}
```

---

## Usage {/*usage*/}

The `"use no memo"` directive is placed at the beginning of a function body to prevent React Compiler from optimizing that function:

```js
function MyComponent() {
  "use no memo";
  // Function body
}
```

The directive can also be placed at the top of a file to affect all functions in that module:

```js
"use no memo";

// All functions in this file will be skipped by the compiler
```

`"use no memo"` at the function level overrides the module level directive.

---

## Troubleshooting {/*troubleshooting*/}

### Directive not preventing compilation {/*not-preventing*/}

If `"use no memo"` isn't working:

```js
// ❌ Wrong - directive after code
function Component() {
  const data = getData();
  "use no memo"; // Too late!
}

// ✅ Correct - directive first
function Component() {
  "use no memo";
  const data = getData();
}
```

Also check:
* Spelling - must be exactly `"use no memo"`
* Quotes - must use single or double quotes, not backticks

### Best practices {/*best-practices*/}

**Always document why** you're disabling optimization:

```js
// ✅ Good - clear explanation and tracking
function DataProcessor() {
  "use no memo"; // TODO: Remove after fixing rule of react violation
  // ...
}

// ❌ Bad - no explanation
function Mystery() {
  "use no memo";
  // ...
}
```

### See also {/*see-also*/}

* [`"use memo"`](/reference/react-compiler/directives/use-memo) - Opt into compilation
* [React Compiler](/learn/react-compiler) - Getting started guide

# Gating

The `gating` option enables conditional compilation, allowing you to control when optimized code is used at runtime.

```js
{
  gating: {
    source: 'my-feature-flags',
    importSpecifierName: 'shouldUseCompiler'
  }
}
```

<InlineToc />

---

## Reference {/*reference*/}

### `gating` {/*gating*/}

Configures runtime feature flag gating for compiled functions.

#### Type {/*type*/}

```
{
  source: string;
  importSpecifierName: string;
} | null
```

#### Default value {/*default-value*/}

`null`

#### Properties {/*properties*/}

- **`source`**: Module path to import the feature flag from
- **`importSpecifierName`**: Name of the exported function to import

#### Caveats {/*caveats*/}

- The gating function must return a boolean
- Both compiled and original versions increase bundle size
- The import is added to every file with compiled functions

---

## Usage {/*usage*/}

### Basic feature flag setup {/*basic-setup*/}

1. Create a feature flag module:

```js
// src/utils/feature-flags.js
export function shouldUseCompiler() {
  // your logic here
  return getFeatureFlag('react-compiler-enabled');
}
```

2. Configure the compiler:

```js
{
  gating: {
    source: './src/utils/feature-flags',
    importSpecifierName: 'shouldUseCompiler'
  }
}
```

3. The compiler generates gated code:

```js
// Input
function Button(props) {
  return <button>{props.label}</button>;
}

// Output (simplified)
import { shouldUseCompiler } from './src/utils/feature-flags';

const Button = shouldUseCompiler()
  ? function Button_optimized(props) { /* compiled version */ }
  : function Button_original(props) { /* original version */ };
```

Note that the gating function is evaluated once at module time, so once the JS bundle has been parsed and evaluated the choice of component stays static for the rest of the browser session.

---

## Troubleshooting {/*troubleshooting*/}

### Feature flag not working {/*flag-not-working*/}

Verify your flag module exports the correct function:

```js
// ❌ Wrong: Default export
export default function shouldUseCompiler() {
  return true;
}

// ✅ Correct: Named export matching importSpecifierName
export function shouldUseCompiler() {
  return true;
}
```

### Import errors {/*import-errors*/}

Ensure the source path is correct:

```js
// ❌ Wrong: Relative to babel.config.js
{
  source: './src/flags',
  importSpecifierName: 'flag'
}

// ✅ Correct: Module resolution path
{
  source: '@myapp/feature-flags',
  importSpecifierName: 'flag'
}

// ✅ Also correct: Absolute path from project root
{
  source: './src/utils/flags',
  importSpecifierName: 'flag'
}
```


# Logger

The `logger` option provides custom logging for React Compiler events during compilation.

```js
{
  logger: {
    logEvent(filename, event) {
      console.log(`[Compiler] ${event.kind}: ${filename}`);
    }
  }
}
```

<InlineToc />

---

## Reference {/*reference*/}

### `logger` {/*logger*/}

Configures custom logging to track compiler behavior and debug issues.

#### Type {/*type*/}

```
{
  logEvent: (filename: string | null, event: LoggerEvent) => void;
} | null
```

#### Default value {/*default-value*/}

`null`

#### Methods {/*methods*/}

- **`logEvent`**: Called for each compiler event with the filename and event details

#### Event types {/*event-types*/}

- **`CompileSuccess`**: Function successfully compiled
- **`CompileError`**: Function skipped due to errors
- **`CompileDiagnostic`**: Non-fatal diagnostic information
- **`CompileSkip`**: Function skipped for other reasons
- **`PipelineError`**: Unexpected compilation error
- **`Timing`**: Performance timing information

#### Caveats {/*caveats*/}

- Event structure may change between versions
- Large codebases generate many log entries

---

## Usage {/*usage*/}

### Basic logging {/*basic-logging*/}

Track compilation success and failures:

```js
{
  logger: {
    logEvent(filename, event) {
      switch (event.kind) {
        case 'CompileSuccess': {
          console.log(`✅ Compiled: ${filename}`);
          break;
        }
        case 'CompileError': {
          console.log(`❌ Skipped: ${filename}`);
          break;
        }
        default: {}
      }
    }
  }
}
```

### Detailed error logging {/*detailed-error-logging*/}

Get specific information about compilation failures:

```js
{
  logger: {
    logEvent(filename, event) {
      if (event.kind === 'CompileError') {
        console.error(`\nCompilation failed: ${filename}`);
        console.error(`Reason: ${event.detail.reason}`);

        if (event.detail.description) {
          console.error(`Details: ${event.detail.description}`);
        }

        if (event.detail.loc) {
          const { line, column } = event.detail.loc.start;
          console.error(`Location: Line ${line}, Column ${column}`);
        }

        if (event.detail.suggestions) {
          console.error('Suggestions:', event.detail.suggestions);
        }
      }
    }
  }
}
```



# Panicthreshold

The `panicThreshold` option controls how the React Compiler handles errors during compilation.

```js
{
  panicThreshold: 'none' // Recommended
}
```

<InlineToc />

---

## Reference {/*reference*/}

### `panicThreshold` {/*panicthreshold*/}

Determines whether compilation errors should fail the build or skip optimization.

#### Type {/*type*/}

```
'none' | 'critical_errors' | 'all_errors'
```

#### Default value {/*default-value*/}

`'none'`

#### Options {/*options*/}

- **`'none'`** (default, recommended): Skip components that can't be compiled and continue building
- **`'critical_errors'`**: Fail the build only on critical compiler errors
- **`'all_errors'`**: Fail the build on any compiler diagnostic

#### Caveats {/*caveats*/}

- Production builds should always use `'none'`
- Build failures prevent your application from building
- The compiler automatically detects and skips problematic code with `'none'`
- Higher thresholds are only useful during development for debugging

---

## Usage {/*usage*/}

### Production configuration (recommended) {/*production-configuration*/}

For production builds, always use `'none'`. This is the default value:

```js
{
  panicThreshold: 'none'
}
```

This ensures:
- Your build never fails due to compiler issues
- Components that can't be optimized run normally
- Maximum components get optimized
- Stable production deployments

### Development debugging {/*development-debugging*/}

Temporarily use stricter thresholds to find issues:

```js
const isDevelopment = process.env.NODE_ENV === 'development';

{
  panicThreshold: isDevelopment ? 'critical_errors' : 'none',
  logger: {
    logEvent(filename, event) {
      if (isDevelopment && event.kind === 'CompileError') {
        // ...
      }
    }
  }
}
```

# Target

The `target` option specifies which React version the compiler should generate code for.

```js
{
  target: '19' // or '18', '17'
}
```

<InlineToc />

---

## Reference {/*reference*/}

### `target` {/*target*/}

Configures the React version compatibility for the compiled output.

#### Type {/*type*/}

```
'17' | '18' | '19'
```

#### Default value {/*default-value*/}

`'19'`

#### Valid values {/*valid-values*/}

- **`'19'`**: Target React 19 (default). No additional runtime required.
- **`'18'`**: Target React 18. Requires `react-compiler-runtime` package.
- **`'17'`**: Target React 17. Requires `react-compiler-runtime` package.

#### Caveats {/*caveats*/}

- Always use string values, not numbers (e.g., `'17'` not `17`)
- Don't include patch versions (e.g., use `'18'` not `'18.2.0'`)
- React 19 includes built-in compiler runtime APIs
- React 17 and 18 require installing `react-compiler-runtime@latest`

---

## Usage {/*usage*/}

### Targeting React 19 (default) {/*targeting-react-19*/}

For React 19, no special configuration is needed:

```js
{
  // defaults to target: '19'
}
```

The compiler will use React 19's built-in runtime APIs:

```js
// Compiled output uses React 19's native APIs
import { c as _c } from 'react/compiler-runtime';
```

### Targeting React 17 or 18 {/*targeting-react-17-or-18*/}

For React 17 and React 18 projects, you need two steps:

1. Install the runtime package:

```bash
npm install react-compiler-runtime@latest
```

2. Configure the target:

```js
// For React 18
{
  target: '18'
}

// For React 17
{
  target: '17'
}
```

The compiler will use the polyfill runtime for both versions:

```js
// Compiled output uses the polyfill
import { c as _c } from 'react-compiler-runtime';
```

---

## Troubleshooting {/*troubleshooting*/}

### Runtime errors about missing compiler runtime {/*missing-runtime*/}

If you see errors like "Cannot find module 'react/compiler-runtime'":

1. Check your React version:
   ```bash
   npm why react
   ```

2. If using React 17 or 18, install the runtime:
   ```bash
   npm install react-compiler-runtime@latest
   ```

3. Ensure your target matches your React version:
   ```js
   {
     target: '18' // Must match your React major version
   }
   ```

### Runtime package not working {/*runtime-not-working*/}

Ensure the runtime package is:

1. Installed in your project (not globally)
2. Listed in your `package.json` dependencies
3. The correct version (`@latest` tag)
4. Not in `devDependencies` (it's needed at runtime)

### Checking compiled output {/*checking-output*/}

To verify the correct runtime is being used, note the different import (`react/compiler-runtime` for builtin, `react-compiler-runtime` standalone package for 17/18):

```js
// For React 19 (built-in runtime)
import { c } from 'react/compiler-runtime'
//                      ^

// For React 17/18 (polyfill runtime)
import { c } from 'react-compiler-runtime'
//                      ^
```