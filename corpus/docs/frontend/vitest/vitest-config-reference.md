<!--
Topics: Vitest configuration, vitest.config.ts, vitest.config.js, test configuration, globals, test environment, jsdom, happy-dom, node environment, coverage, setupFiles, include patterns, exclude patterns, test timeout, threads, pool, workspace
Keywords: configure vitest, vitest config, test environment, jsdom setup, coverage setup, setup files, test patterns, test timeout, vitest options, config file
-->
# Vitest Configuration Reference

<!-- Source: alias.md -->


## alias

- **Type:** `Record<string, string> | Array<{ find: string | RegExp, replacement: string, customResolver?: ResolverFunction | ResolverObject }>`

Define custom aliases when running inside tests. They will be merged with aliases from `resolve.alias`.

 warning
Vitest uses Vite SSR primitives to run tests which has [certain pitfalls](https://vitejs.dev/guide/ssr.html#ssr-externals).

1. Aliases affect only modules imported directly with an `import` keyword by an [inlined](#server-deps-inline) module (all source code is inlined by default).
2. Vitest does not support aliasing `require` calls.
3. If you are aliasing an external dependency (e.g., `react` -> `preact`), you may want to alias the actual `node_modules` packages instead to make it work for externalized dependencies. Both [Yarn](https://classic.yarnpkg.com/en/docs/cli/add/#toc-yarn-add-alias) and [pnpm](https://pnpm.io/aliases/) support aliasing via the `npm:` prefix.



<!-- Source: allowonly.md -->


## allowOnly

- **Type**: `boolean`
- **Default**: `!process.env.CI`
- **CLI:** `--allowOnly`, `--allowOnly=false`

By default, Vitest does not permit tests marked with the [`only`](/api/test#test-only) flag in Continuous Integration (CI) environments. Conversely, in local development environments, Vitest allows these tests to run.

 info
Vitest uses [`std-env`](https://www.npmjs.com/package/std-env) package to detect the environment.


You can customize this behavior by explicitly setting the `allowOnly` option to either `true` or `false`.

 code-group
```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    allowOnly: true,
  },
})
```
```bash [CLI]
vitest --allowOnly
```


When enabled, Vitest will not fail the test suite if tests marked with [`only`](/api/test#test-only) are detected, including in CI environments.

When disabled, Vitest will fail the test suite if tests marked with [`only`](/api/test#test-only) are detected, including in local development environments.


<!-- Source: attachmentsdir.md -->


## attachmentsDir

- **Type:** `string`
- **Default:** `'.vitest-attachments'`

Directory path for storing attachments created by [`context.annotate`](/guide/test-context#annotate) relative to the project root.


<!-- Source: bail.md -->


## bail

- **Type:** `number`
- **Default:** `0`
- **CLI**: `--bail=<value>`

Stop test execution when given number of tests have failed.

By default Vitest will run all of your test cases even if some of them fail. This may not be desired for CI builds where you are only interested in 100% successful builds and would like to stop test execution as early as possible when test failures occur. The `bail` option can be used to speed up CI runs by preventing it from running more tests when failures have occurred.


<!-- Source: cache.md -->


## cache <CRoot />

- **Type**: `false`
- **CLI**: `--no-cache`, `--cache=false`

Use this option if you want to disable the cache feature. At the moment Vitest stores cache for test results to run the longer and failed tests first.

The cache directory is controlled by the Vite's [`cacheDir`](https://vitejs.dev/config/shared-options.html#cachedir) option:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  cacheDir: 'custom-folder/.vitest'
})
```

You can limit the directory only for Vitest by using `process.env.VITEST`:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  cacheDir: process.env.VITEST ? 'custom-folder/.vitest' : undefined
})
```


<!-- Source: chaiconfig.md -->


## chaiConfig

- **Type:** `{ includeStack?, showDiff?, truncateThreshold? }`
- **Default:** `{ includeStack: false, showDiff: true, truncateThreshold: 40 }`

Equivalent to [Chai config](https://github.com/chaijs/chai/blob/4.x.x/lib/chai/config.js).

## chaiConfig.includeStack

- **Type:** `boolean`
- **Default:** `false`

Influences whether stack trace is included in Assertion error message. Default of false suppresses stack trace in the error message.

## chaiConfig.showDiff

- **Type:** `boolean`
- **Default:** `true`

Influences whether or not the `showDiff` flag should be included in the thrown AssertionErrors. `false` will always be `false`; `true` will be true when the assertion has requested a diff to be shown.

## chaiConfig.truncateThreshold

- **Type:** `number`
- **Default:** `40`

Sets length threshold for actual and expected values in assertion errors. If this threshold is exceeded, for example for large data structures, the value is replaced with something like `[ Array(3) ]` or `{ Object (prop1, prop2) }`. Set it to `0` if you want to disable truncating altogether.

This config option affects truncating values in `test.each` titles and inside the assertion error message.


<!-- Source: clearmocks.md -->


## clearMocks

- **Type:** `boolean`
- **Default:** `false`

Should Vitest automatically call [`vi.clearAllMocks()`](/api/vi#vi-clearallmocks) before each test.

This will clear mock history without affecting mock implementations.

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    clearMocks: true,
  },
})
```


<!-- Source: dangerouslyignoreunhandlederrors.md -->


## dangerouslyIgnoreUnhandledErrors <CRoot />

- **Type**: `boolean`
- **Default**: `false`
- **CLI:**
  - `--dangerouslyIgnoreUnhandledErrors`
  - `--dangerouslyIgnoreUnhandledErrors=false`

If this option is set to `true`, Vitest will not fail the test run if there are unhandled errors. Note that built-in reporters will still report them.

If you want to filter out certain errors conditionally, use [`onUnhandledError`](/config/onunhandlederror) callback instead.

## Example

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    dangerouslyIgnoreUnhandledErrors: true,
  },
})
```


<!-- Source: detectasyncleaks.md -->


## detectAsyncLeaks

- **Type:** `boolean`
- **CLI:** `--detectAsyncLeaks`, `--detect-async-leaks`
- **Default:** `false`

 warning
Enabling this option will make your tests run much slower. Use only when debugging or developing tests.


Detect asynchronous resources leaking from the test file.
Uses [`node:async_hooks`](https://nodejs.org/api/async_hooks.html) to track creation of async resources. If a resource is not cleaned up, it will be logged after tests have finished.

For example if your code has `setTimeout` calls that execute the callback after tests have finished, you will see following error:

```sh
⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯ Async Leaks 1 ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯

Timeout leaking in test/checkout-screen.test.tsx
 26|
 27|   useEffect(() => {
 28|     setTimeout(() => setWindowWidth(window.innerWidth), 150)
   |     ^
 29|   })
 30|
```

To fix this, you'll need to make sure your code cleans the timeout properly:

```js
useEffect(() => {
  setTimeout(() => setWindowWidth(window.innerWidth), 150) // 
  const timeout = setTimeout(() => setWindowWidth(window.innerWidth), 150) // 

  return function cleanup() { // 
    clearTimeout(timeout) // 
  } // 
})
```


<!-- Source: diff.md -->


## diff

- **Type:** `string`
- **CLI:** `--diff=<path>`

`DiffOptions` object or a path to a module which exports `DiffOptions`. Useful if you want to customize diff display.

For example, as a config object:

```ts
import { defineConfig } from 'vitest/config'
import c from 'picocolors'

export default defineConfig({
  test: {
    diff: {
      aIndicator: c.bold('--'),
      bIndicator: c.bold('++'),
      omitAnnotationLines: true,
    },
  },
})
```

Or as a module:

code-group
```ts [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    diff: './vitest.diff.ts',
  },
})
```

```ts [vitest.diff.ts]
import type { DiffOptions } from 'vitest'
import c from 'picocolors'

export default {
  aIndicator: c.bold('--'),
  bIndicator: c.bold('++'),
  omitAnnotationLines: true,
} satisfies DiffOptions
```


## diff.expand

- **Type**: `boolean`
- **Default**: `true`
- **CLI:** `--diff.expand=false`

Expand all common lines.

## diff.truncateThreshold

- **Type**: `number`
- **Default**: `0`
- **CLI:** `--diff.truncateThreshold=<path>`

The maximum length of diff result to be displayed. Diffs above this threshold will be truncated.
Truncation won't take effect with default value 0.

## diff.truncateAnnotation

- **Type**: `string`
- **Default**: `'... Diff result is truncated'`
- **CLI:** `--diff.truncateAnnotation=<annotation>`

Annotation that is output at the end of diff result if it's truncated.

## diff.truncateAnnotationColor

- **Type**: `DiffOptionsColor = (arg: string) => string`
- **Default**: `noColor = (string: string): string => string`

Color of truncate annotation, default is output with no color.

## diff.printBasicPrototype

- **Type**: `boolean`
- **Default**: `false`

Print basic prototype `Object` and `Array` in diff output

## diff.maxDepth

- **Type**: `number`
- **Default**: `20` (or `8` when comparing different types)

Limit the depth to recurse when printing nested objects


<!-- Source: dir.md -->


## dir

- **Type:** `string`
- **CLI:** `--dir=<path>`
- **Default:** same as `root`

Base directory to scan for the test files. You can specify this option to speed up test discovery if your root covers the whole project


<!-- Source: disableconsoleintercept.md -->


## disableConsoleIntercept

- **Type:** `boolean`
- **CLI:** `--disableConsoleIntercept`
- **Default:** `false`

By default, Vitest automatically intercepts console logging during tests for extra formatting of test file, test title, etc.

This is also required for console log preview on Vitest UI.

However, disabling such interception might help when you want to debug a code with normal synchronous terminal console logging.

 warning
This option has no effect on [browser tests](/guide/browser/) since Vitest preserves original logging in browser devtools.



<!-- Source: env.md -->


## env

- **Type:** `Partial<NodeJS.ProcessEnv>`

Environment variables available on `process.env` and `import.meta.env` during tests. These variables will not be available in the main process (in `globalSetup`, for example).


<!-- Source: environment.md -->


## environment

- **Type:** `'node' | 'jsdom' | 'happy-dom' | 'edge-runtime' | string`
- **Default:** `'node'`
- **CLI:** `--environment=<env>`

The environment that will be used for testing. The default environment in Vitest
is a Node.js environment. If you are building a web application, you can use
browser-like environment through either [`jsdom`](https://github.com/jsdom/jsdom)
or [`happy-dom`](https://github.com/capricorn86/happy-dom) instead.
If you are building edge functions, you can use [`edge-runtime`](https://edge-runtime.vercel.app/packages/vm) environment

 tip
You can also use [Browser Mode](/guide/browser/) to run integration or unit tests in the browser without mocking the environment.


To define custom options for your environment, use [`environmentOptions`](/config/environmentoptions).

By adding a `@vitest-environment` docblock or comment at the top of the file,
you can specify another environment to be used for all tests in that file:

Docblock style:

```js
/**
 * @vitest-environment jsdom
 */

test('use jsdom in this test file', () => {
  const element = document.createElement('div')
  expect(element).not.toBeNull()
})
```

Comment style:

```js
// @vitest-environment happy-dom

test('use happy-dom in this test file', () => {
  const element = document.createElement('div')
  expect(element).not.toBeNull()
})
```

For compatibility with Jest, there is also a `@jest-environment`:

```js
/**
 * @jest-environment jsdom
 */

test('use jsdom in this test file', () => {
  const element = document.createElement('div')
  expect(element).not.toBeNull()
})
```

You can also define a custom environment. When non-builtin environment is used, Vitest will try to load the file if it's relative or absolute, or a package `vitest-environment-${name}`, if the name is a bare specifier.

The custom environment file should export an object with the shape of `Environment`:

```ts [environment.js]
import type { Environment } from 'vitest'

export default <Environment>{
  name: 'custom',
  viteEnvironment: 'ssr',
  setup() {
    // custom setup
    return {
      teardown() {
        // called after all tests with this env have been run
      }
    }
  }
}
```

 tip
The `viteEnvironment` field corresponde to the environment defined by the [Vite Environment API](https://vite.dev/guide/api-environment#environment-api). By default, Vite exposes `client` (for the browser) and `ssr` (for the server) environments.


Vitest also exposes `builtinEnvironments` through `vitest/environments` entry, in case you just want to extend it. You can read more about extending environments in [our guide](/guide/environment).

 tip
jsdom environment exposes `jsdom` global variable equal to the current [JSDOM](https://github.com/jsdom/jsdom) instance. If you want TypeScript to recognize it, you can add `vitest/jsdom` to your `tsconfig.json` when you use this environment:

```json [tsconfig.json]
{
  "compilerOptions": {
    "types": ["vitest/jsdom"]
  }
}
```



<!-- Source: environmentoptions.md -->


## environmentOptions

- **Type:** `Record<'jsdom' | 'happyDOM' | string, unknown>`
- **Default:** `{}`

These options are passed to the setup method of the current [environment](/config/environment). By default, you can configure options only for `jsdom` and `happyDOM` when you use them as your test environment.

## Example

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environmentOptions: {
      jsdom: {
        url: 'http://localhost:3000',
      },
      happyDOM: {
        width: 300,
        height: 400,
      },
    },
  },
})
```

 warning
Options are scoped to their environment. For example, put jsdom options under the `jsdom` key and happy-dom options under the `happyDOM` key. This lets you mix multiple environments within the same project.



<!-- Source: exclude.md -->


## exclude

- **Type:** `string[]`
- **Default:** `['**/node_modules/**', '**/.git/**']`
- **CLI:** `vitest --exclude "**/excluded-file" --exclude "*/other-files/*.js"`

A list of [glob patterns](https://superchupu.dev/tinyglobby/comparison) that should be excluded from your test files. These patterns are resolved relative to the [`root`](/config/root) ([`process.cwd()`](https://nodejs.org/api/process.html#processcwd) by default).

Vitest uses the [`tinyglobby`](https://www.npmjs.com/package/tinyglobby) package to resolve the globs.

 warning
This option does not affect coverage. If you need to remove certain files from the coverage report, use [`coverage.exclude`](/config/coverage#exclude).

This is the only option that doesn't override your configuration if you provide it with a CLI flag. All glob patterns added via `--exclude` flag will be added to the config's `exclude`.


## Example

```js
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      './temp/**',
    ],
  },
})
```

 tip
Although the CLI `exclude` option is additive, manually setting `exclude` in your config will replace the default value. To extend the default `exclude` patterns, use `configDefaults` from `vitest/config`:

```js{6}
import { configDefaults, defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    exclude: [
      ...configDefaults.exclude,
      'packages/template/*',
      './temp/**',
    ],
  },
})
```



<!-- Source: execargv.md -->


## execArgv

- **Type:** `string[]`
- **Default:** `[]`

Pass additional arguments to `node` in the runner worker. See [Command-line API | Node.js](https://nodejs.org/docs/latest/api/cli.html) for more information.

> **Warning:** Be careful when using, it as some options may crash worker, e.g. `--prof`, `--title`. See https://github.com/nodejs/node/issues/41103.



<!-- Source: expandsnapshotdiff.md -->


## expandSnapshotDiff

- **Type:** `boolean`
- **CLI:** `--expandSnapshotDiff`, `--expand-snapshot-diff`
- **Default:** `false`

Show full diff when snapshot fails instead of a patch.


<!-- Source: faketimers.md -->


## fakeTimers

- **Type:** `FakeTimerInstallOpts`

Options that Vitest will pass down to [`@sinon/fake-timers`](https://www.npmjs.com/package/@sinonjs/fake-timers) when using [`vi.useFakeTimers()`](/api/vi#vi-usefaketimers).

## fakeTimers.now

- **Type:** `number | Date`
- **Default:** `Date.now()`

Installs fake timers with the specified Unix epoch.

## fakeTimers.toFake

- **Type:** `('setTimeout' | 'clearTimeout' | 'setImmediate' | 'clearImmediate' | 'setInterval' | 'clearInterval' | 'Date' | 'nextTick' | 'hrtime' | 'requestAnimationFrame' | 'cancelAnimationFrame' | 'requestIdleCallback' | 'cancelIdleCallback' | 'performance' | 'queueMicrotask')[]`
- **Default:** everything available globally except `nextTick` and `queueMicrotask`

An array with names of global methods and APIs to fake.

To only mock `setTimeout()` and `nextTick()`, specify this property as `['setTimeout', 'nextTick']`.

Mocking `nextTick` is not supported when running Vitest inside `node:child_process` by using `--pool=forks`. NodeJS uses `process.nextTick` internally in `node:child_process` and hangs when it is mocked. Mocking `nextTick` is supported when running Vitest with `--pool=threads`.

## fakeTimers.loopLimit

- **Type:** `number`
- **Default:** `10_000`

The maximum number of timers that will be run when calling [`vi.runAllTimers()`](/api/vi#vi-runalltimers).

## fakeTimers.shouldAdvanceTime

- **Type:** `boolean`
- **Default:** `false`

Tells @sinonjs/fake-timers to increment mocked time automatically based on the real system time shift (e.g. the mocked time will be incremented by 20ms for every 20ms change in the real system time).

## fakeTimers.advanceTimeDelta

- **Type:** `number`
- **Default:** `20`

Relevant only when using with `shouldAdvanceTime: true`. increment mocked time by advanceTimeDelta ms every advanceTimeDelta ms change in the real system time.

## fakeTimers.shouldClearNativeTimers

- **Type:** `boolean`
- **Default:** `true`

Tells fake timers to clear "native" (i.e. not fake) timers by delegating to their respective handlers. When disabled, it can lead to potentially unexpected behavior if timers existed prior to starting fake timers session.


<!-- Source: fileparallelism.md -->


## fileParallelism

- **Type:** `boolean`
- **Default:** `true`
- **CLI:** `--no-file-parallelism`, `--fileParallelism=false`

Should all test files run in parallel. Setting this to `false` will override `maxWorkers` option to `1`.

 tip
This option doesn't affect tests running in the same file. If you want to run those in parallel, use `concurrent` option on [describe](/api/describe#describe-concurrent) or via [a config](#sequence-concurrent).



<!-- Source: forcereruntriggers.md -->


## forceRerunTriggers <CRoot />

- **Type**: `string[]`
- **Default:** `['**/package.json/**', '**/vitest.config.*/**', '**/vite.config.*/**']`

Glob pattern of file paths that will trigger the whole suite rerun. When paired with the `--changed` argument will run the whole test suite if the trigger is found in the git diff.

Useful if you are testing calling CLI commands, because Vite cannot construct a module graph:

```ts
test('execute a script', async () => {
  // Vitest cannot rerun this test, if content of `dist/index.js` changes
  await execa('node', ['dist/index.js'])
})
```

 tip
Make sure that your files are not excluded by [`server.watch.ignored`](https://vitejs.dev/config/server-options.html#server-watch).



<!-- Source: globals.md -->


## globals

- **Type:** `boolean`
- **Default:** `false`
- **CLI:** `--globals`, `--no-globals`, `--globals=false`

By default, `vitest` does not provide global APIs for explicitness. If you prefer to use the APIs globally like Jest, you can pass the `--globals` option to CLI or add `globals: true` in the config.

```js
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
  },
})
```

 tip
Note that some libraries, e.g., `@testing-library/react`, rely on globals being present to perform auto cleanup.


To get TypeScript working with the global APIs, add `vitest/globals` to the `types` field in your `tsconfig.json`:

```json [tsconfig.json]
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

If you have redefined your [`typeRoots`](https://www.typescriptlang.org/tsconfig/#typeRoots) to include additional types in your compilation, you will need to add back the `node_modules` to make `vitest/globals` discoverable:

```json [tsconfig.json]
{
  "compilerOptions": {
    "typeRoots": ["./types", "./node_modules/@types", "./node_modules"],
    "types": ["vitest/globals"]
  }
}
```


<!-- Source: globalsetup.md -->


## globalSetup

- **Type:** `string | string[]`

Path to global setup files relative to project [root](/config/root).

A global setup file can either export named functions `setup` and `teardown` or a `default` function that returns a teardown function:

 code-group
```js [exports]
export function setup(project) {
  console.log('setup')
}

export function teardown() {
  console.log('teardown')
}
```
```js [default]
export default function setup(project) {
  console.log('setup')

  return function teardown() {
    console.log('teardown')
  }
}
```


Note that the `setup` method and a `default` function receive a [test project](/api/advanced/test-project) as the first argument. The global setup is called before the test workers are created and only if there is at least one test queued, and teardown is called after all test files have finished running. In [watch mode](/config/watch), the teardown is called before the process is exited instead. If you need to reconfigure your setup before the test rerun, you can use [`onTestsRerun`](#handling-test-reruns) hook instead.

Multiple global setup files are possible. `setup` and `teardown` are executed sequentially with teardown in reverse order.

 danger
Beware that the global setup is running in a different global scope before test workers are even created, so your tests don't have access to global variables defined here. However, you can pass down serializable data to tests via [`provide`](/config/provide) method and read them in your tests via `inject` imported from `vitest`:

code-group
```ts [example.test.ts]
import { inject } from 'vitest'

inject('wsPort') === 3000
```
```ts [globalSetup.ts]
import type { TestProject } from 'vitest/node'

export default function setup(project: TestProject) {
  project.provide('wsPort', 3000)
}

declare module 'vitest' {
  export interface ProvidedContext {
    wsPort: number
  }
}
```

If you need to execute code in the same process as tests, use [`setupFiles`](/config/setupfiles) instead, but note that it runs before every test file.


### Handling Test Reruns

You can define a custom callback function to be called when Vitest reruns tests. The test runner will wait for it to complete before executing tests. Note that you cannot destruct the `project` like `{ onTestsRerun }` because it relies on the context.

```ts [globalSetup.ts]
import type { TestProject } from 'vitest/node'

export default function setup(project: TestProject) {
  project.onTestsRerun(async () => {
    await restartDb()
  })
}
```


<!-- Source: hideskippedtests.md -->


## hideSkippedTests

- **Type:** `boolean`
- **CLI:** `--hideSkippedTests`, `--hide-skipped-tests`
- **Default:** `false`

Hide logs for skipped tests


<!-- Source: hooktimeout.md -->


## hookTimeout

- **Type:** `number`
- **Default:** `10_000` in Node.js, `30_000` if `browser.enabled` is `true`
- **CLI:** `--hook-timeout=10000`, `--hookTimeout=10000`

Default timeout of a hook in milliseconds. Use `0` to disable timeout completely.


<!-- Source: include-source.md -->


## includeSource

- **Type:** `string[]`
- **Default:** `[]`

A list of [glob patterns](https://superchupu.dev/tinyglobby/comparison) that match your [in-source test files](/guide/in-source). These patterns are resolved relative to the [`root`](/config/root) ([`process.cwd()`](https://nodejs.org/api/process.html#processcwd) by default).

When defined, Vitest will run all matched files that have `import.meta.vitest` inside.

 warning
Vitest performs a simple text-based inclusion check on source files. If a file contains `import.meta.vitest`, even in a comment, it will be matched as an in-source test file.


Vitest uses the [`tinyglobby`](https://www.npmjs.com/package/tinyglobby) package to resolve the globs.

## Example

```js
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    includeSource: ['src/**/*.{js,ts}'],
  },
})
```

Then you can write tests inside your source files:

```ts [src/index.ts]
export function add(...args: number[]) {
  return args.reduce((a, b) => a + b, 0)
}

// #region in-source test suites
if (import.meta.vitest) {
  const { it, expect } = import.meta.vitest
  it('add', () => {
    expect(add()).toBe(0)
    expect(add(1)).toBe(1)
    expect(add(1, 2, 3)).toBe(6)
  })
}
// #endregion
```

For your production build, you need to replace the `import.meta.vitest` with `undefined`, letting the bundler do the dead code elimination.

 code-group
```js [vite.config.ts]
import { defineConfig } from 'vite'

export default defineConfig({
  define: { // 
    'import.meta.vitest': 'undefined', // 
  }, // 
})
```
```js [rolldown.config.js]
import { defineConfig } from 'rolldown/config'

export default defineConfig({
  transform: {
    define: { // 
      'import.meta.vitest': 'undefined', // 
    }, // 
  },
})
```
```js [rollup.config.js]
import replace from '@rollup/plugin-replace' // 

export default {
  plugins: [
    replace({ // 
      'import.meta.vitest': 'undefined', // 
    }) // 
  ],
  // other options
}
```
```js [build.config.js]
import { defineBuildConfig } from 'unbuild'

export default defineBuildConfig({
  replace: { // 
    'import.meta.vitest': 'undefined', // 
  }, // 
  // other options
})
```
```js [webpack.config.js]
const webpack = require('webpack')

module.exports = {
  plugins: [
    new webpack.DefinePlugin({ // 
      'import.meta.vitest': 'undefined', // 
    })// 
  ],
}
```


 tip
To get TypeScript support for `import.meta.vitest`, add `vitest/importMeta` to your `tsconfig.json`:

```json [tsconfig.json]
{
  "compilerOptions": {
    "types": ["vitest/importMeta"]
  }
}
```



<!-- Source: include.md -->


## include

- **Type:** `string[]`
- **Default:** `['**/*.{test,spec}.?(c|m)[jt]s?(x)']`
- **CLI:** `vitest [...include]`, `vitest **/*.test.js`

A list of [glob patterns](https://superchupu.dev/tinyglobby/comparison) that match your test files. These patterns are resolved relative to the [`root`](/config/root) ([`process.cwd()`](https://nodejs.org/api/process.html#processcwd) by default).

Vitest uses the [`tinyglobby`](https://www.npmjs.com/package/tinyglobby) package to resolve the globs.

 tip NOTE
When using coverage, Vitest automatically adds test files `include` patterns to coverage's default `exclude` patterns. See [`coverage.exclude`](/config/coverage#exclude).


## Example

```js
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: [
      './test',
      './**/*.{test,spec}.tsx?',
    ],
  },
})
```

Vitest provides reasonable defaults, so normally you wouldn't override them. A good example of defining `include` is for [test projects](/guide/projects):

```js{8,12} [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'unit',
          include: ['./test/unit/*.test.js'],
        },
      },
      {
        test: {
          name: 'e2e',
          include: ['./test/e2e/*.test.js'],
        },
      },
    ],
  },
})
```

 warning
This option will override Vitest defaults. If you just want to extend them, use `configDefaults` from `vitest/config`:

```js{6}
import { configDefaults, defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: [
      ...configDefaults.include,
      './test',
      './**/*.{test,spec}.tsx?',
    ],
  },
})
```



<!-- Source: includetasklocation.md -->


## includeTaskLocation

- **Type:** `boolean`
- **Default:** `false`

Should `location` property be included when Vitest API receives tasks in [reporters](#reporters). If you have a lot of tests, this might cause a small performance regression.

The `location` property has `column` and `line` values that correspond to the `test` or `describe` position in the original file.

This option will be auto-enabled if you don't disable it explicitly, and you are running Vitest with:
- [Vitest UI](/guide/ui)
- or using the [Browser Mode](/guide/browser/) without [headless](/guide/browser/#headless) mode
- or using [HTML Reporter](/guide/reporters#html-reporter)

 tip
This option has no effect if you do not use custom code that relies on this.



<!-- Source: logheapusage.md -->


## logHeapUsage

- **Type**: `boolean`
- **Default**: `false`
- **CLI:** `--logHeapUsage`, `--logHeapUsage=false`

Show heap usage after each test. Useful for debugging memory leaks.


<!-- Source: maxconcurrency.md -->


## maxConcurrency

- **Type**: `number`
- **Default**: `5`
- **CLI**: `--max-concurrency=10`, `--maxConcurrency=10`

A number of tests that are allowed to run at the same time marked with `test.concurrent`.

Test above this limit will be queued to run when available slot appears.


<!-- Source: maxworkers.md -->


## maxWorkers

- **Type:** `number | string`
- **Default:**
  - if [`watch`](/config/watch) is disabled, uses all available parallelism
  - if [`watch`](/config/watch) is enabled, uses half of all available parallelism

Defines the maximum concurrency for test workers. Accepts either a number or a percentage string.

- Number: spawns up to the specified number of workers.
- Percentage string (e.g., "50%"): computes the worker count as the given percentage of the machine’s available parallelism.

## Example

### Number

 code-group
```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    maxWorkers: 4,
  },
})
```
```bash [CLI]
vitest --maxWorkers=4
```


### Percent

 code-group
```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    maxWorkers: '50%',
  },
})
```
```bash [CLI]
vitest --maxWorkers=50%
```


Vitest uses [`os.availableParallelism`](https://nodejs.org/api/os.html#osavailableparallelism) to know the maximum amount of parallelism available.


<!-- Source: mockreset.md -->


## mockReset

- **Type:** `boolean`
- **Default:** `false`

Should Vitest automatically call [`vi.resetAllMocks()`](/api/vi#vi-resetallmocks) before each test.

This will clear mock history and reset each implementation.

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    mockReset: true,
  },
})
```


<!-- Source: mode.md -->


## mode

- **Type:** `string`
- **CLI:** `--mode=staging`
- **Default:** `'test'`

Overrides Vite mode


<!-- Source: name.md -->


## name

- **Type:**

```ts
interface UserConfig {
  name?: string | { label: string; color?: LabelColor }
}
```

Assign a custom name to the test project or Vitest process. The name will be visible in the CLI and UI, and available in the Node.js API via [`project.name`](/api/advanced/test-project#name).

The color used by the CLI and UI can be changed by providing an object with a `color` property.

## Colors

The displayed colors depend on your terminal’s color scheme. In the UI, colors match their CSS equivalents.

- black
- red
- green
- yellow
- blue
- magenta
- cyan
- white

## Example

 code-group
```js [string]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    name: 'unit',
  },
})
```
```js [object]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    name: {
      label: 'unit',
      color: 'blue',
    },
  },
})
```


This property is mostly useful if you have several projects as it helps distinguish them in your terminal:

```js{7,11} [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      {
        name: 'unit',
        include: ['./test/*.unit.test.js'],
      },
      {
        name: 'e2e',
        include: ['./test/*.e2e.test.js'],
      },
    ],
  },
})
```

 tip
Vitest automatically assigns a name when none is provided. Resolution order:

- If the project is specified by a config file or directory, Vitest uses the package.json's `name` field.
- If there is no `package.json`, Vitest falls back to the project folder's basename.
- If the project is defined inline in the `projects` array (an object), Vitest assigns a numeric name equal to that project's array index (0-based).


 warning
Note that projects cannot have the same name. Vitest will throw an error during the config resolution.


You can also assign different names to different browser [instances](/config/browser/instances):

```js{10,11} [vitest.config.js]
import { defineConfig } from 'vitest/config'
import { playwright } from '@vitest/browser-playwright'

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: playwright(),
      instances: [
        { browser: 'chromium', name: 'Chrome' },
        { browser: 'firefox', name: 'Firefox' },
      ],
    },
  },
})
```

 tip
Browser instances inherit their parent project's name with the browser name appended in parentheses. For example, a project named `browser` with a chromium instance will be shown as `browser (chromium)`.

If the parent project has no name, or instances are defined at the root level (not inside a named project), the instance name defaults to the browser value (e.g. `chromium`). To override this behavior, set an explicit `name` on the instance.



<!-- Source: onconsolelog.md -->


## onConsoleLog <CRoot />

```ts
function onConsoleLog(
  log: string,
  type: 'stdout' | 'stderr',
  entity: TestModule | TestSuite | TestCase | undefined,
): boolean | void
```

Custom handler for `console` methods in tests. If you return `false`, Vitest will not print the log to the console. Note that Vitest ignores all other falsy values.

Can be useful for filtering out logs from third-party libraries.

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    onConsoleLog(log: string, type: 'stdout' | 'stderr'): boolean | void {
      return !(log === 'message from third party library' && type === 'stdout')
    },
  },
})
```


<!-- Source: onstacktrace.md -->


## onStackTrace <CRoot />

- **Type**: `(error: Error, frame: ParsedStack) => boolean | void`

Apply a filtering function to each frame of each stack trace when handling errors. This does not apply to stack traces printed by [`printConsoleTrace`](/config/printconsoletrace#printconsoletrace). The first argument, `error`, is a `TestError`.

Can be useful for filtering out stack trace frames from third-party libraries.

 tip
The stack trace's total size is also typically limited by V8's [`Error.stackTraceLimit`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/stackTraceLimit) number. You could set this to a high value in your test setup function to prevent stacks from being truncated.


```ts
import type { ParsedStack, TestError } from 'vitest'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    onStackTrace(error: TestError, { file }: ParsedStack): boolean | void {
      // If we've encountered a ReferenceError, show the whole stack.
      if (error.name === 'ReferenceError') {
        return
      }

      // Reject all frames from third party libraries.
      if (file.includes('node_modules')) {
        return false
      }
    },
  },
})
```


<!-- Source: onunhandlederror.md -->


## onUnhandledError <CRoot /> <Version>4.0.0</Version>

- **Type:**

```ts
function onUnhandledError(
  error: (TestError | Error) & { type: string }
): boolean | void
```

A custom callback for filtering unhandled errors that should not be reported. When an error is filtered out, it no longer affects the result of the test run.

To report unhandled errors without affecting the test outcome, use the [`dangerouslyIgnoreUnhandledErrors`](/config/dangerouslyignoreunhandlederrors) option instead.

 tip
This callback is called on the main thread, it doesn't have access to your test context.


## Example

```ts
import type { ParsedStack } from 'vitest'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    onUnhandledError(error): boolean | void {
      // Ignore all errors with the name "MySpecialError".
      if (error.name === 'MySpecialError') {
        return false
      }
    },
  },
})
```


<!-- Source: open.md -->


## open <CRoot />

- **Type:** `boolean`
- **Default:** `!process.env.CI`
- **CLI:** `--open`, `--open=false`

Open Vitest UI automatically if it's [enabled](/config/ui).


<!-- Source: outputfile.md -->


## outputFile <CRoot />

- **Type:** `string | Record<string, string>`
- **CLI:** `--outputFile=<path>`, `--outputFile.json=./path`

Write test results to a file when the `--reporter=json`, `--reporter=html` or `--reporter=junit` option is also specified.
By providing an object instead of a string you can define individual outputs when using multiple reporters.


<!-- Source: passwithnotests.md -->


## passWithNoTests <CRoot />

- **Type**: `boolean`
- **Default**: `false`
- **CLI:** `--passWithNoTests`, `--passWithNoTests=false`

Vitest will not fail, if no tests will be found.


<!-- Source: pool.md -->


## pool

- **Type:** `'threads' | 'forks' | 'vmThreads' | 'vmForks'`
- **Default:** `'forks'`
- **CLI:** `--pool=threads`

Pool used to run tests in.

## threads

Enable multi-threading. When using threads you are unable to use process related APIs such as `process.chdir()`. Some libraries written in native languages, such as Prisma, `bcrypt` and `canvas`, have problems when running in multiple threads and run into segfaults. In these cases it is advised to use `forks` pool instead.

## forks

Similar as `threads` pool but uses `child_process` instead of `worker_threads`. Communication between tests and main process is not as fast as with `threads` pool. Process related APIs such as `process.chdir()` are available in `forks` pool.

## vmThreads

Run tests using [VM context](https://nodejs.org/api/vm.html) (inside a sandboxed environment) in a `threads` pool.

This makes tests run faster, but the VM module is unstable when running [ESM code](https://github.com/nodejs/node/issues/37648). Your tests will [leak memory](https://github.com/nodejs/node/issues/33439) - to battle that, consider manually editing [`vmMemoryLimit`](/config/vmmemorylimit) value.

 warning
Running code in a sandbox has some advantages (faster tests), but also comes with a number of disadvantages.

- The globals within native modules, such as (`fs`, `path`, etc), differ from the globals present in your test environment. As a result, any error thrown by these native modules will reference a different Error constructor compared to the one used in your code:

```ts
try {
  fs.writeFileSync('/doesnt exist')
}
catch (err) {
  console.log(err instanceof Error) // false
}
```

- Importing ES modules caches them indefinitely which introduces memory leaks if you have a lot of contexts (test files). There is no API in Node.js that clears that cache.
- Accessing globals [takes longer](https://github.com/nodejs/node/issues/31658) in a sandbox environment.

Please, be aware of these issues when using this option. Vitest team cannot fix any of the issues on our side.


## vmForks

Similar as `vmThreads` pool but uses `child_process` instead of `worker_threads`. Communication between tests and the main process is not as fast as with `vmThreads` pool. Process related APIs such as `process.chdir()` are available in `vmForks` pool. Please be aware that this pool has the same pitfalls listed in `vmThreads`.


<!-- Source: printconsoletrace.md -->


## printConsoleTrace

- **Type:** `boolean`
- **Default:** `false`

Always print console traces when calling any `console` method. This is useful for debugging.


<!-- Source: projects.md -->


## projects <CRoot />

- **Type:** `TestProjectConfiguration[]`
- **Default:** `[]`

An array of [projects](/guide/projects).


<!-- Source: provide.md -->


## provide

- **Type:** `Partial<ProvidedContext>`

Define values that can be accessed inside your tests using `inject` method.

code-group
```ts [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    provide: {
      API_KEY: '123',
    },
  },
})
```
```ts [api.test.js]
import { expect, inject, test } from 'vitest'

test('api key is defined', () => {
  expect(inject('API_KEY')).toBe('123')
})
```


 warning
Properties have to be strings and values need to be [serializable](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Structured_clone_algorithm#supported_types) because this object will be transferred between different processes.


 tip
If you are using TypeScript, you will need to augment `ProvidedContext` type for type safe access:

```ts [vitest.shims.d.ts]
declare module 'vitest' {
  export interface ProvidedContext {
    API_KEY: string
  }
}

// mark this file as a module so augmentation works correctly
export {}
```



<!-- Source: reporters.md -->


## reporters <CRoot />

- **Type:**

```ts
interface UserConfig {
  reporters?: ConfigReporter | Array<ConfigReporter>
}

type ConfigReporter = string | Reporter | [string, object?]
```

- **Default:** [`'default'`](/guide/reporters#default-reporter)
- **CLI:**
  - `--reporter=tap` for a single reporter
  - `--reporter=verbose --reporter=github-actions` for multiple reporters

This option defines a single reporter or a list of reporters available to Vitest during the test run.

Alongside built-in reporters, you can also pass down a custom implementation of a [`Reporter` interface](/api/advanced/reporters), or a path to a module that exports it as a default export (e.g. `'./path/to/reporter.ts'`, `'@scope/reporter'`).

You can configure a reporter by providing a tuple: `[string, object]`, where the string is a reporter name, and the object is the reporter's options.

 warning
Note that the [coverage](/guide/coverage) feature uses a different [`coverage.reporter`](/config/coverage#reporter) option instead of this one.


## Built-in Reporters

- [`default`](/guide/reporters#default-reporter)
- [`verbose`](/guide/reporters#verbose-reporter)
- [`tree`](/guide/reporters#tree-reporter)
- [`dot`](/guide/reporters#dot-reporter)
- [`junit`](/guide/reporters#junit-reporter)
- [`json`](/guide/reporters#json-reporter)
- [`html`](/guide/reporters#html-reporter)
- [`tap`](/guide/reporters#tap-reporter)
- [`tap-flat`](/guide/reporters#tap-flat-reporter)
- [`hanging-process`](/guide/reporters#hanging-process-reporter)
- [`github-actions`](/guide/reporters#github-actions-reporter)
- [`blob`](/guide/reporters#blob-reporter)

## Example

 code-group
```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    reporters: [
      'default',
      // conditional reporter
      process.env.CI ? 'github-actions' : {},
      // custom reporter from npm package
      // options are passed down as a tuple
      [
        'vitest-sonar-reporter',
        { outputFile: 'sonar-report.xml' }
      ],
    ]
  }
})
```
```bash [CLI]
vitest --reporter=github-actions --reporter=junit
```



<!-- Source: resolvesnapshotpath.md -->


## resolveSnapshotPath <CRoot />

- **Type**: `(testPath: string, snapExtension: string, context: { config: SerializedConfig }) => string`
- **Default**: stores snapshot files in `__snapshots__` directory

Overrides default snapshot path. For example, to store snapshots next to test files:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    resolveSnapshotPath: (testPath, snapExtension) => testPath + snapExtension,
  },
})
```

You can also use the `context` parameter to access the project's serialized config. This is useful when you have multiple [projects](/guide/projects) and want to store snapshots in different locations based on the project name:

```ts
import { basename, dirname, join } from 'node:path'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    resolveSnapshotPath(testPath, snapExtension, context) {
      return join(
        dirname(testPath),
        '__snapshots__',
        context.config.name ?? 'default',
        basename(testPath) + snapExtension,
      )
    },
  },
})
```


<!-- Source: restoremocks.md -->


## restoreMocks

- **Type:** `boolean`
- **Default:** `false`

Should Vitest automatically call [`vi.restoreAllMocks()`](/api/vi#vi-restoreallmocks) before each test.

This restores all original implementations on spies created manually with [`vi.spyOn`](/api/vi#vi-spyon).

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    restoreMocks: true,
  },
})
```


<!-- Source: retry.md -->


## retry

Retry the test specific number of times if it fails.

- **Type:** `number | { count?: number, delay?: number, condition?: RegExp }`
- **Default:** `0`
- **CLI:** `--retry <times>`, `--retry.count <times>`, `--retry.delay <ms>`, `--retry.condition <pattern>`

## Basic Usage

Specify a number to retry failed tests:

```ts
export default defineConfig({
  test: {
    retry: 3,
  },
})
```

## CLI Usage

You can also configure retry options from the command line:

```bash
# Simple retry count
vitest --retry 3

# Advanced options using dot notation
vitest --retry.count 3 --retry.delay 500 --retry.condition 'ECONNREFUSED|timeout'
```

## Advanced Options <Version>4.1.0</Version>

Use an object to configure retry behavior:

```ts
export default defineConfig({
  test: {
    retry: {
      count: 3, // Number of times to retry
      delay: 1000, // Delay in milliseconds between retries
      condition: /ECONNREFUSED|timeout/i, // RegExp to match errors that should trigger retry
    },
  },
})
```

### count

Number of times to retry a test if it fails. Default is `0`.

```ts
export default defineConfig({
  test: {
    retry: {
      count: 2,
    },
  },
})
```

### delay

Delay in milliseconds between retry attempts. Useful for tests that interact with rate-limited APIs or need time to recover. Default is `0`.

```ts
export default defineConfig({
  test: {
    retry: {
      count: 3,
      delay: 500, // Wait 500ms between retries
    },
  },
})
```

### condition

A RegExp pattern or a function to determine if a test should be retried based on the error.

- When a **RegExp**, it's tested against the error message
- When a **function**, it receives the error and returns a boolean

 warning
When defining `condition` as a function, it must be done in a test file directly, not in a configuration file (configurations are serialized for worker threads).


#### RegExp condition (in config file):

```ts
export default defineConfig({
  test: {
    retry: {
      count: 2,
      condition: /ECONNREFUSED|ETIMEDOUT/i, // Retry on connection/timeout errors
    },
  },
})
```

#### Function condition (in test file):

```ts
import { describe, test } from 'vitest'

describe('tests with advanced retry condition', () => {
  test('with function condition', { retry: { count: 2, condition: error => error.message.includes('Network') } }, () => {
    // test code
  })
})
```

## Test File Override

You can also define retry options per test or suite in test files:

```ts
import { describe, test } from 'vitest'

describe('flaky tests', {
  retry: {
    count: 2,
    delay: 100,
  },
}, () => {
  test('network request', () => {
    // test code
  })
})

test('another test', {
  retry: {
    count: 3,
    condition: error => error.message.includes('timeout'),
  },
}, () => {
  // test code
})
```


<!-- Source: root.md -->


## root

- **Type:** `string`
- **CLI:** `-r <path>`, `--root=<path>`

Project root


<!-- Source: runner.md -->


## runner

- **Type**: `VitestRunnerConstructor`
- **Default**: `node`, when running tests, or `benchmark`, when running benchmarks

Path to a custom test runner. This is an advanced feature and should be used with custom library runners. You can read more about it in [the documentation](/api/advanced/runner).


<!-- Source: sequence.md -->


## sequence

- **Type**: `{ sequencer?, shuffle?, seed?, hooks?, setupFiles?, groupOrder }`

Options for how tests should be sorted.

You can provide sequence options to CLI with dot notation:

```sh
npx vitest --sequence.shuffle --sequence.seed=1000
```

## sequence.sequencer <CRoot />

- **Type**: `TestSequencerConstructor`
- **Default**: `BaseSequencer`

A custom class that defines methods for sharding and sorting. You can extend `BaseSequencer` from `vitest/node`, if you only need to redefine one of the `sort` and `shard` methods, but both should exist.

Sharding is happening before sorting, and only if `--shard` option is provided.

If [`sequencer.groupOrder`](#grouporder) is specified, the sequencer will be called once for each group and pool.

## sequence.groupOrder

- **Type:** `number`
- **Default:** `0`

Controls the order in which this project runs its tests when using multiple [projects](/guide/projects).

- Projects with the same group order number will run together, and groups are run from lowest to highest.
- If you don't set this option, all projects run in parallel.
- If several projects use the same group order, they will run at the same time.

This setting only affects the order in which projects run, not the order of tests within a project.
To control test isolation or the order of tests inside a project, use the [`isolate`](#isolate) and [`sequence.sequencer`](#sequence-sequencer) options.

 details Example
Consider this example:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'slow',
          sequence: {
            groupOrder: 0,
          },
        },
      },
      {
        test: {
          name: 'fast',
          sequence: {
            groupOrder: 0,
          },
        },
      },
      {
        test: {
          name: 'flaky',
          sequence: {
            groupOrder: 1,
          },
        },
      },
    ],
  },
})
```

Tests in these projects will run in this order:

```
 0. slow  |
          |> running together
 0. fast  |

 1. flaky |> runs after slow and fast alone
```


## sequence.shuffle

- **Type**: `boolean | { files?, tests? }`
- **Default**: `false`
- **CLI**: `--sequence.shuffle`, `--sequence.shuffle=false`

If you want files and tests to run randomly, you can enable it with this option, or CLI argument [`--sequence.shuffle`](/guide/cli).

Vitest usually uses cache to sort tests, so long-running tests start earlier, which makes tests run faster. If your files and tests run in random order, you will lose this performance improvement, but it may be useful to track tests that accidentally depend on another test run previously.

### sequence.shuffle.files

- **Type**: `boolean`
- **Default**: `false`
- **CLI**: `--sequence.shuffle.files`, `--sequence.shuffle.files=false`

Whether to randomize files, be aware that long running tests will not start earlier if you enable this option.

### sequence.shuffle.tests

- **Type**: `boolean`
- **Default**: `false`
- **CLI**: `--sequence.shuffle.tests`, `--sequence.shuffle.tests=false`

Whether to randomize tests.

## sequence.concurrent

- **Type**: `boolean`
- **Default**: `false`
- **CLI**: `--sequence.concurrent`, `--sequence.concurrent=false`

If you want tests to run in parallel, you can enable it with this option, or CLI argument [`--sequence.concurrent`](/guide/cli).

 warning
When you run tests with `sequence.concurrent` and `expect.requireAssertions` set to `true`, you should use [local expect](/guide/test-context.html#expect) instead of the global one. Otherwise, this may cause false negatives in [some situations (#8469)](https://github.com/vitest-dev/vitest/issues/8469).


## sequence.seed <CRoot />

- **Type**: `number`
- **Default**: `Date.now()`
- **CLI**: `--sequence.seed=1000`

Sets the randomization seed, if tests are running in random order.

## sequence.hooks

- **Type**: `'stack' | 'list' | 'parallel'`
- **Default**: `'stack'`
- **CLI**: `--sequence.hooks=<value>`

Changes the order in which hooks are executed.

- `stack` will order "after" hooks in reverse order, "before" hooks will run in the order they were defined
- `list` will order all hooks in the order they are defined
- `parallel` will run hooks in a single group in parallel (hooks in parent suites will still run before the current suite's hooks)

 tip
This option doesn't affect [`onTestFinished`](/api/hooks#ontestfinished). It is always called in reverse order.


## sequence.setupFiles

- **Type**: `'list' | 'parallel'`
- **Default**: `'parallel'`
- **CLI**: `--sequence.setupFiles=<value>`

Changes the order in which setup files are executed.

- `list` will run setup files in the order they are defined
- `parallel` will run setup files in parallel


<!-- Source: server.md -->


## server <Deprecated />

Before Vitest 4, this option was used to define the configuration for the `vite-node` server.

At the moment, this option allows you to configure the inlining and externalization mechanisms, along with the module runner debugging configuration.

 warning
These options should be used only as the last resort to improve performance by externalizing auto-inlined dependencies or to fix issues by inlining invalid external dependencies.

Normally, Vitest should do this automatically.


## deps

### external

- **Type:** `(string | RegExp)[]`
- **Default:** files inside [`moduleDirectories`](/config/deps#moduledirectories)

Specifies modules that should not be transformed by Vite and should instead be processed directly by the engine. These modules are imported via native dynamic `import` and bypass both transformation and resolution phases.

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    server: {
      deps: {
        external: ['react'],
      },
    },
  },
})
```

External modules and their dependencies are not present in the module graph and will not trigger test restarts when they change.

Typically, packages under `node_modules` are externalized.

 tip
If a string is provided, it is first normalized by prefixing the `/node_modules/` or other [`moduleDirectories`](/config/deps#moduledirectories) segments (for example, `'react'` becomes `/node_modules/react/`), and the resulting string is then matched against the full file path. For example, package `@company/some-name` located inside `packages/some-name` should be specified as `some-name`, and `packages` should be included in `deps.moduleDirectories`.

If a `RegExp` is provided, it is matched against the full file path.


### inline

- **Type:** `(string | RegExp)[] | true`
- **Default:** everything that is not externalized

Specifies modules that should be transformed and resolved by Vite. These modules are run by Vite's [module runner](https://vite.dev/guide/api-environment-runtimes#modulerunner).

Typically, your source files are inlined.

 tip
If a string is provided, it is first normalized by prefixing the `/node_modules/` or other [`moduleDirectories`](/config/deps#moduledirectories) segments (for example, `'react'` becomes `/node_modules/react/`), and the resulting string is then matched against the full file path. For example, package `@company/some-name` located inside `packages/some-name` should be specified as `some-name`, and `packages` should be included in `deps.moduleDirectories`.

If a `RegExp` is provided, it is matched against the full file path.


### fallbackCJS

- **Type:** `boolean`
- **Default:** `false`

When enabled, Vitest will try to guess a CommonJS build for an ESM entry by checking a few common CJS/UMD file name and folder patterns (like `.mjs`, `.umd.js`, `.cjs.js`, `umd/`, `cjs/`, `lib/`).

This is a best-effort heuristic to work around confusing or incorrect ESM/CJS packaging and may not work for all dependencies.


<!-- Source: setupfiles.md -->


## setupFiles

- **Type:** `string | string[]`

Paths to setup files resolved relative to the [`root`](/config/root). They will run before each _test file_ in the same process. By default, all test files run in parallel, but you can configure it with [`sequence.setupFiles`](/config/sequence#sequence-setupfiles) option.

Vitest will ignore any exports from these files.

> **Warning:** Note that setup files are executed in the same process as tests, unlike [`globalSetup`](/config/globalsetup) that runs once in the main thread before any test worker is created.


> **Info:** Editing a setup file will automatically trigger a rerun of all tests.


If you have a heavy process running in the background, you can use `process.env.VITEST_POOL_ID` (integer-like string) inside to distinguish between workers and spread the workload.

> **Warning:** If [isolation](/config/isolate) is disabled, imported modules are cached, but the setup file itself is executed again before each test file, meaning that you are accessing the same global object before each test file. Make sure you are not doing the same thing more than necessary.

For example, you may rely on a global variable:

```ts
import { config } from '@some-testing-lib'

if (!globalThis.setupInitialized) {
  config.plugins = [myCoolPlugin]
  computeHeavyThing()
  globalThis.setupInitialized = true
}

// hooks reset before each test file
afterEach(() => {
  cleanup()
})

globalThis.resetBeforeEachTest = true
```



<!-- Source: silent.md -->


## silent <CRoot />

- **Type:** `boolean | 'passed-only'`
- **Default:** `false`
- **CLI:** `--silent`, `--silent=false`

Silent console output from tests.

Use `'passed-only'` to see logs from failing tests only. Logs from failing tests are printed after a test has finished.


<!-- Source: slowtestthreshold.md -->


## slowTestThreshold <CRoot />

- **Type**: `number`
- **Default**: `300`
- **CLI**: `--slow-test-threshold=<number>`, `--slowTestThreshold=<number>`

The number of milliseconds after which a test or suite is considered slow and reported as such in the results.


<!-- Source: snapshotenvironment.md -->


## snapshotEnvironment

- **Type:** `string`

Path to a custom snapshot environment implementation. This is useful if you are running your tests in an environment that doesn't support Node.js APIs. This option doesn't have any effect on a browser runner.

This object should have the shape of `SnapshotEnvironment` and is used to resolve and read/write snapshot files:

```ts
export interface SnapshotEnvironment {
  getVersion: () => string
  getHeader: () => string
  resolvePath: (filepath: string) => Promise<string>
  resolveRawPath: (testPath: string, rawPath: string) => Promise<string>
  saveSnapshotFile: (filepath: string, snapshot: string) => Promise<void>
  readSnapshotFile: (filepath: string) => Promise<string | null>
  removeSnapshotFile: (filepath: string) => Promise<void>
}
```

You can extend default `VitestSnapshotEnvironment` from `vitest/snapshot` entry point if you need to overwrite only a part of the API.

 warning
This is a low-level option and should be used only for advanced cases where you don't have access to default Node.js APIs.

If you just need to configure snapshots feature, use [`snapshotFormat`](#snapshotformat) or [`resolveSnapshotPath`](#resolvesnapshotpath) options.



<!-- Source: snapshotformat.md -->


## snapshotFormat <CRoot />

- **Type:** `PrettyFormatOptions`

Format options for snapshot testing. These options are passed down to our fork of [`pretty-format`](https://www.npmjs.com/package/pretty-format). In addition to the `pretty-format` options we support `printShadowRoot: boolean`.

 tip
Beware that `plugins` field on this object will be ignored.

If you need to extend snapshot serializer via pretty-format plugins, please, use [`expect.addSnapshotSerializer`](/api/expect#expect-addsnapshotserializer) API or [snapshotSerializers](#snapshotserializers) option.



<!-- Source: snapshotserializers.md -->


## snapshotSerializers <CRoot />

- **Type:** `string[]`
- **Default:** `[]`

A list of paths to snapshot serializer modules for snapshot testing, useful if you want add custom snapshot serializers. See [Custom Serializer](/guide/snapshot#custom-serializer) for more information.


<!-- Source: stricttags.md -->


## strictTags <Version>4.1.0</Version>

- **Type:** `boolean`
- **Default:** `true`
- **CLI:** `--strict-tags`, `--no-strict-tags`

Should Vitest throw an error if test has a [`tag`](/config/tags) that is not defined in the config to avoid silently doing something surprising due to mistyped names (applying the wrong configuration or skipping the test due to a `--tags-filter` flag).

Note that Vitest will always throw an error if `--tags-filter` flag defines a tag not present in the config.

For example, this test will throw an error because the tag `fortnend` has a typo (it should be `frontend`):

 code-group
```js [form.test.js]
test('renders a form', { tags: ['fortnend'] }, () => {
  // ...
})
```
```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    tags: [
      { name: 'frontend' },
    ],
  },
})
```



<!-- Source: tags.md -->


## tags <Version>4.1.0</Version>

- **Type:** `TestTagDefinition[]`
- **Default:** `[]`

Defines all [available tags](/guide/test-tags) in your test project. By default, if test defines a name not listed here, Vitest will throw an error, but this can be configured via a [`strictTags`](/config/stricttags) option.

If you are using [`projects`](/config/projects), they will inherit all global tags definitions automatically.

Use [`--tags-filter`](/guide/test-tags#syntax) to filter tests by their tags. Use [`--list-tags`](/guide/cli#listtags) to print every tag in your Vitest workspace.

## name

- **Type:** `string`
- **Required:** `true`

The name of the tag. This is what you use in the `tags` option in tests.

```ts
export default defineConfig({
  test: {
    tags: [
      { name: 'unit' },
      { name: 'e2e' },
    ],
  },
})
```

 tip
If you are using TypeScript, you can enforce what tags are available by augmenting the `TestTags` type with a property that contains a union of strings (make sure this file is included by your `tsconfig`):

```ts [vitest.shims.ts]
import 'vitest'

declare module 'vitest' {
  interface TestTags {
    tags:
      | 'frontend'
      | 'backend'
      | 'db'
      | 'flaky'
  }
}
```


## description

- **Type:** `string`

A human-readable description for the tag. This will be shown in UI and inside error messages when a tag is not found.

```ts
export default defineConfig({
  test: {
    tags: [
      {
        name: 'slow',
        description: 'Tests that take a long time to run.',
      },
    ],
  },
})
```

## priority

- **Type:** `number`
- **Default:** `Infinity`

Priority for merging options when multiple tags with the same options are applied to a test. Lower number means higher priority (e.g., priority `1` takes precedence over priority `3`).

```ts
export default defineConfig({
  test: {
    tags: [
      {
        name: 'flaky',
        timeout: 30_000,
        priority: 1, // higher priority
      },
      {
        name: 'db',
        timeout: 60_000,
        priority: 2, // lower priority
      },
    ],
  },
})
```

When a test has both tags, the `timeout` will be `30_000` because `flaky` has a higher priority.

## Test Options

Tags can define [test options](/api/test#test-options) that will be applied to every test marked with the tag. These options are merged with the test's own options, with the test's options taking precedence.

 warning
The [`retry.condition`](/api/test#retry) can onle be a regexp because the config values need to be serialised.

Tags also cannot apply other [tags](/api/test#tags) via these options.


## Example

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    tags: [
      {
        name: 'unit',
        description: 'Unit tests.',
      },
      {
        name: 'e2e',
        description: 'End-to-end tests.',
        timeout: 60_000,
      },
      {
        name: 'flaky',
        description: 'Flaky tests that need retries.',
        retry: process.env.CI ? 3 : 0,
        priority: 1,
      },
      {
        name: 'slow',
        description: 'Slow tests.',
        timeout: 120_000,
      },
      {
        name: 'skip-ci',
        description: 'Tests to skip in CI.',
        skip: !!process.env.CI,
      },
    ],
  },
})
```


<!-- Source: teardowntimeout.md -->


## teardownTimeout <CRoot />

- **Type:** `number`
- **Default:** `10000`
- **CLI:** `--teardown-timeout=5000`, `--teardownTimeout=5000`

Default timeout to wait for close when Vitest shuts down, in milliseconds


<!-- Source: testnamepattern.md -->


## testNamePattern <CRoot />

- **Type** `string | RegExp`
- **CLI:** `-t <pattern>`, `--testNamePattern=<pattern>`, `--test-name-pattern=<pattern>`

Run tests with full names matching the pattern.
If you add `OnlyRunThis` to this property, tests not containing the word `OnlyRunThis` in the test name will be skipped.

```js
import { expect, test } from 'vitest'

// run
test('OnlyRunThis', () => {
  expect(true).toBe(true)
})

// skipped
test('doNotRun', () => {
  expect(true).toBe(true)
})
```


<!-- Source: testtimeout.md -->


## testTimeout

- **Type:** `number`
- **Default:** `5_000` in Node.js, `15_000` if `browser.enabled` is `true`
- **CLI:** `--test-timeout=5000`, `--testTimeout=5000`

Default timeout of a test in milliseconds. Use `0` to disable timeout completely.


<!-- Source: unstubenvs.md -->


## unstubEnvs

- **Type:** `boolean`
- **Default:** `false`

Should Vitest automatically call [`vi.unstubAllEnvs()`](/api/vi#vi-unstuballenvs) before each test.

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    unstubEnvs: true,
  },
})
```


<!-- Source: unstubglobals.md -->


## unstubGlobals

- **Type:** `boolean`
- **Default:** `false`

Should Vitest automatically call [`vi.unstubAllGlobals()`](/api/vi#vi-unstuballglobals) before each test.

```js [vitest.config.js]
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    unstubGlobals: true,
  },
})
```


<!-- Source: update.md -->


## update <CRoot />

- **Type:** `boolean | 'new' | 'all'`
- **Default:** `false`
- **CLI:** `-u`, `--update`, `--update=false`, `--update=new`

Update snapshot files. The behaviour depends on the value:

- `true` or `'all'`: updates all changed snapshots and delete obsolete ones
- `new`: generates new snapshots without changing or deleting obsolete ones


<!-- Source: vmmemorylimit.md -->


## vmMemoryLimit

- **Type:** `string | number`
- **Default:** `1 / CPU Cores`

This option affects only `vmForks` and `vmThreads` pools.

Specifies the memory limit for workers before they are recycled. This value heavily depends on your environment, so it's better to specify it manually instead of relying on the default.

 tip
The implementation is based on Jest's [`workerIdleMemoryLimit`](https://jestjs.io/docs/configuration#workeridlememorylimit-numberstring).

The limit can be specified in a number of different ways and whatever the result is `Math.floor` is used to turn it into an integer value:

- `<= 1` - The value is assumed to be a percentage of system memory. So 0.5 sets the memory limit of the worker to half of the total system memory
- `\> 1` - Assumed to be a fixed byte value. Because of the previous rule if you wanted a value of 1 byte (I don't know why) you could use 1.1.
- With units
  - `50%` - As above, a percentage of total system memory
  - `100KB`, `65MB`, etc - With units to denote a fixed memory limit.
    - `K` / `KB` - Kilobytes (x1000)
    - `KiB` - Kibibytes (x1024)
    - `M` / `MB` - Megabytes
    - `MiB` - Mebibytes
    - `G` / `GB` - Gigabytes
    - `GiB` - Gibibytes


 warning
Percentage based memory limit [does not work on Linux CircleCI](https://github.com/jestjs/jest/issues/11956#issuecomment-1212925677) workers due to incorrect system memory being reported.



<!-- Source: watch.md -->


## watch <CRoot />

- **Type:** `boolean`
- **Default:** `!process.env.CI && process.stdin.isTTY`
- **CLI:** `-w`, `--watch`, `--watch=false`

Enable watch mode

In interactive environments, this is the default, unless `--run` is specified explicitly.

In CI, or when run from a non-interactive shell, "watch" mode is not the default, but can be enabled explicitly with this flag.


<!-- Source: watchtriggerpatterns.md -->


## watchTriggerPatterns <CRoot /> <Version>3.2.0</Version>

- **Type:** `WatcherTriggerPattern[]`

Vitest reruns tests based on the module graph which is populated by static and dynamic `import` statements. However, if you are reading from the file system or fetching from a proxy, then Vitest cannot detect those dependencies.

To correctly rerun those tests, you can define a regex pattern and a function that returns a list of test files to run.

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    watchTriggerPatterns: [
      {
        pattern: /^src\/(mailers|templates)\/(.*)\.(ts|html|txt)$/,
        testsToRun: (id, match) => {
          // relative to the root value
          return `./api/tests/mailers/${match[2]}.test.ts`
        },
      },
    ],
  },
})
```

 warning
Returned files should be either absolute or relative to the root. Note that this is a global option, and it cannot be used inside of [project](/guide/projects) configs.



<!-- Source: deps.md -->


## deps

- **Type:** `{ optimizer?, ... }`

Handling for dependencies resolution.

## deps.optimizer

- **Type:** `{ ssr?, client? }`
- **See also:** [Dep Optimization Options](https://vitejs.dev/config/dep-optimization-options.html)

Enable dependency optimization. If you have a lot of tests, this might improve their performance.

When Vitest encounters the external library listed in `include`, it will be bundled into a single file using esbuild and imported as a whole module. This is good for several reasons:

- Importing packages with a lot of imports is expensive. By bundling them into one file we can save a lot of time
- Importing UI libraries is expensive because they are not meant to run inside Node.js
- Your `alias` configuration is now respected inside bundled packages
- Code in your tests is running closer to how it's running in the browser

Be aware that only packages in `deps.optimizer?.[mode].include` option are bundled (some plugins populate this automatically, like Svelte). You can read more about available options in [Vite](https://vitejs.dev/config/dep-optimization-options.html) docs (Vitest doesn't support `disable` and `noDiscovery` options). By default, Vitest uses `optimizer.client` for `jsdom` and `happy-dom` environments, and `optimizer.ssr` for `node` and `edge` environments.

This options also inherits your `optimizeDeps` configuration (for web Vitest will extend `optimizeDeps`, for ssr - `ssr.optimizeDeps`). If you redefine `include`/`exclude` option in `deps.optimizer` it will extend your `optimizeDeps` when running tests. Vitest automatically removes the same options from `include`, if they are listed in `exclude`.

 tip
You will not be able to edit your `node_modules` code for debugging, since the code is actually located in your `cacheDir` or `test.cache.dir` directory. If you want to debug with `console.log` statements, edit it directly or force rebundling with `deps.optimizer?.[mode].force` option.


### deps.optimizer.{mode}.enabled

- **Type:** `boolean`
- **Default:** `false`

Enable dependency optimization.

## deps.client

- **Type:** `{ transformAssets?, ... }`

Options that are applied to external files when the environment is set to `client`. By default, `jsdom` and `happy-dom` use `client` environment, while `node` and `edge` environments use `ssr`, so these options will have no affect on files inside those environments.

Usually, files inside `node_modules` are externalized, but these options also affect files in [`server.deps.external`](#server-deps-external).

### deps.client.transformAssets

- **Type:** `boolean`
- **Default:** `true`

Should Vitest process assets (.png, .svg, .jpg, etc) files and resolve them like Vite does in the browser.

This module will have a default export equal to the path to the asset, if no query is specified.

 warning
At the moment, this option only works with [`vmThreads`](#vmthreads) and [`vmForks`](#vmforks) pools.


### deps.client.transformCss

- **Type:** `boolean`
- **Default:** `true`

Should Vitest process CSS (.css, .scss, .sass, etc) files and resolve them like Vite does in the browser.

If CSS files are disabled with [`css`](#css) options, this option will just silence `ERR_UNKNOWN_FILE_EXTENSION` errors.

 warning
At the moment, this option only works with [`vmThreads`](#vmthreads) and [`vmForks`](#vmforks) pools.


### deps.client.transformGlobPattern

- **Type:** `RegExp | RegExp[]`
- **Default:** `[]`

Regexp pattern to match external files that should be transformed.

By default, files inside `node_modules` are externalized and not transformed, unless it's CSS or an asset, and corresponding option is not disabled.

 warning
At the moment, this option only works with [`vmThreads`](#vmthreads) and [`vmForks`](#vmforks) pools.


## deps.interopDefault

- **Type:** `boolean`
- **Default:** `true`

Interpret CJS module's default as named exports. Some dependencies only bundle CJS modules and don't use named exports that Node.js can statically analyze when a package is imported using `import` syntax instead of `require`. When importing such dependencies in Node environment using named exports, you will see this error:

```
import { read } from 'fs-jetpack';
         ^^^^
SyntaxError: Named export 'read' not found. The requested module 'fs-jetpack' is a CommonJS module, which may not support all module.exports as named exports.
CommonJS modules can always be imported via the default export.
```

Vitest doesn't do static analysis, and cannot fail before your running code, so you will most likely see this error when running tests, if this feature is disabled:

```
TypeError: createAsyncThunk is not a function
TypeError: default is not a function
```

By default, Vitest assumes you are using a bundler to bypass this and will not fail, but you can disable this behaviour manually, if your code is not processed.

## deps.moduleDirectories

- **Type:** `string[]`
- **Default**: `['node_modules']`

A list of directories that should be treated as module directories. This config option affects the behavior of [`vi.mock`](/api/vi#vi-mock): when no factory is provided and the path of what you are mocking matches one of the `moduleDirectories` values, Vitest will try to resolve the mock by looking for a `__mocks__` folder in the [root](#root) of the project.

This option will also affect if a file should be treated as a module when externalizing dependencies. By default, Vitest imports external modules with native Node.js bypassing Vite transformation step.

Setting this option will _override_ the default, if you wish to still search `node_modules` for packages include it along with any other options:

```ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    deps: {
      moduleDirectories: ['node_modules', path.resolve('../../packages')],
    }
  },
})
```


<!-- Source: coverage.md -->


## coverage <CRoot />

You can use [`v8`](/guide/coverage.html#v8-provider), [`istanbul`](/guide/coverage.html#istanbul-provider) or [a custom coverage solution](/guide/coverage#custom-coverage-provider) for coverage collection.

You can provide coverage options to CLI with dot notation:

```sh
npx vitest --coverage.enabled --coverage.provider=istanbul
```

 warning
If you are using coverage options with dot notation, don't forget to specify `--coverage.enabled`. Do not provide a single `--coverage` option in that case.


## coverage.provider

- **Type:** `'v8' | 'istanbul' | 'custom'`
- **Default:** `'v8'`
- **CLI:** `--coverage.provider=<provider>`

Use `provider` to select the tool for coverage collection.

## coverage.enabled

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.enabled`, `--coverage.enabled=false`

Enables coverage collection. Can be overridden using `--coverage` CLI option.

## coverage.include

- **Type:** `string[]`
- **Default:** Files that were imported during test run
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.include=<pattern>`, `--coverage.include=<pattern1> --coverage.include=<pattern2>`

List of files included in coverage as glob patterns. By default only files covered by tests are included.

It is recommended to pass file extensions in the pattern.

See [Including and excluding files from coverage report](/guide/coverage.html#including-and-excluding-files-from-coverage-report) for examples.

## coverage.exclude

- **Type:** `string[]`
- **Default:** : `[]`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.exclude=<path>`, `--coverage.exclude=<path1> --coverage.exclude=<path2>`

List of files excluded from coverage as glob patterns.

See [Including and excluding files from coverage report](/guide/coverage.html#including-and-excluding-files-from-coverage-report) for examples.

## coverage.clean

- **Type:** `boolean`
- **Default:** `true`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.clean`, `--coverage.clean=false`

Clean coverage results before running tests

## coverage.cleanOnRerun

- **Type:** `boolean`
- **Default:** `true`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.cleanOnRerun`, `--coverage.cleanOnRerun=false`

Clean coverage report on watch rerun. Set to `false` to preserve coverage results from previous run in watch mode.

## coverage.reportsDirectory

- **Type:** `string`
- **Default:** `'./coverage'`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.reportsDirectory=<path>`

 warning
Vitest will delete this directory before running tests if `coverage.clean` is enabled (default value).


Directory to write coverage report to.

To preview the coverage report in the output of [HTML reporter](/guide/reporters.html#html-reporter), this option must be set as a sub-directory of the html report directory (for example `./html/coverage`).

## coverage.reporter

- **Type:** `string | string[] | [string, {}][]`
- **Default:** `['text', 'html', 'clover', 'json']`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.reporter=<reporter>`, `--coverage.reporter=<reporter1> --coverage.reporter=<reporter2>`

Coverage reporters to use. See [istanbul documentation](https://istanbul.js.org/docs/advanced/alternative-reporters/) for detailed list of all reporters. See [`@types/istanbul-reports`](https://github.com/DefinitelyTyped/DefinitelyTyped/blob/276d95e4304b3670eaf6e8e5a7ea9e265a14e338/types/istanbul-reports/index.d.ts) for details about reporter specific options.

The reporter has three different types:

- A single reporter: `{ reporter: 'html' }`
- Multiple reporters without options: `{ reporter: ['html', 'json'] }`
- A single or multiple reporters with reporter options:
  <!-- eslint-skip -->
  ```ts
  {
    reporter: [
      ['lcov', { 'projectRoot': './src' }],
      ['json', { 'file': 'coverage.json' }],
      ['text']
    ]
  }
  ```

You can also pass custom coverage reporters. See [Guide - Custom Coverage Reporter](/guide/coverage#custom-coverage-reporter) for more information.

<!-- eslint-skip -->
```ts
  {
    reporter: [
      // Specify reporter using name of the NPM package
      '@vitest/custom-coverage-reporter',
      ['@vitest/custom-coverage-reporter', { someOption: true }],

      // Specify reporter using local path
      '/absolute/path/to/custom-reporter.cjs',
      ['/absolute/path/to/custom-reporter.cjs', { someOption: true }],
    ]
  }
```

You can check your coverage report in Vitest UI: check [Vitest UI Coverage](/guide/coverage#vitest-ui) for more details.

## coverage.reportOnFailure

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.reportOnFailure`, `--coverage.reportOnFailure=false`

Generate coverage report even when tests fail.

## coverage.allowExternal

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.allowExternal`, `--coverage.allowExternal=false`

Collect coverage of files outside the [project `root`](#root).

## coverage.excludeAfterRemap

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.excludeAfterRemap`, `--coverage.excludeAfterRemap=false`

Apply exclusions again after coverage has been remapped to original sources.
This is useful when your source files are transpiled and may contain source maps of non-source files.

Use this option when you are seeing files that show up in report even if they match your `coverage.exclude` patterns.

## coverage.skipFull

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.skipFull`, `--coverage.skipFull=false`

Do not show files with 100% statement, branch, and function coverage.

## coverage.thresholds

Options for coverage thresholds.

If a threshold is set to a positive number, it will be interpreted as the minimum percentage of coverage required. For example, setting the lines threshold to `90` means that 90% of lines must be covered.

If a threshold is set to a negative number, it will be treated as the maximum number of uncovered items allowed. For example, setting the lines threshold to `-10` means that no more than 10 lines may be uncovered.

<!-- eslint-skip -->
```ts
{
  coverage: {
    thresholds: {
      // Requires 90% function coverage
      functions: 90,

      // Require that no more than 10 lines are uncovered
      lines: -10,
    }
  }
}
```

### coverage.thresholds.lines

- **Type:** `number`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.lines=<number>`

Global threshold for lines.

### coverage.thresholds.functions

- **Type:** `number`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.functions=<number>`

Global threshold for functions.

### coverage.thresholds.branches

- **Type:** `number`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.branches=<number>`

Global threshold for branches.

### coverage.thresholds.statements

- **Type:** `number`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.statements=<number>`

Global threshold for statements.

### coverage.thresholds.perFile

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.perFile`, `--coverage.thresholds.perFile=false`

Check thresholds per file.

### coverage.thresholds.autoUpdate

- **Type:** `boolean | function`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.autoUpdate=<boolean>`

Update all threshold values `lines`, `functions`, `branches` and `statements` to configuration file when current coverage is better than the configured thresholds.
This option helps to maintain thresholds when coverage is improved.

You can also pass a function for formatting the updated threshold values:

<!-- eslint-skip -->
```ts
{
  coverage: {
    thresholds: {
      // Update thresholds without decimals
      autoUpdate: (newThreshold) => Math.floor(newThreshold),

      // 95.85 -> 95
      functions: 95,
    }
  }
}
```

### coverage.thresholds.100

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.thresholds.100`, `--coverage.thresholds.100=false`

Sets global thresholds to 100.
Shortcut for `--coverage.thresholds.lines 100 --coverage.thresholds.functions 100 --coverage.thresholds.branches 100 --coverage.thresholds.statements 100`.

### coverage.thresholds[glob-pattern]

- **Type:** `{ statements?: number functions?: number branches?: number lines?: number }`
- **Default:** `undefined`
- **Available for providers:** `'v8' | 'istanbul'`

Sets thresholds for files matching the glob pattern.

 tip NOTE
Vitest counts all files, including those covered by glob-patterns, into the global coverage thresholds.
This is different from Jest behavior.


<!-- eslint-skip -->
```ts
{
  coverage: {
    thresholds: {
      // Thresholds for all files
      functions: 95,
      branches: 70,

      // Thresholds for matching glob pattern
      'src/utils/**.ts': {
        statements: 95,
        functions: 90,
        branches: 85,
        lines: 80,
      },

      // Files matching this pattern will only have lines thresholds set.
      // Global thresholds are not inherited.
      '**/math.ts': {
        lines: 100,
      }
    }
  }
}
```

### coverage.thresholds[glob-pattern].100

- **Type:** `boolean`
- **Default:** `false`
- **Available for providers:** `'v8' | 'istanbul'`

Sets thresholds to 100 for files matching the glob pattern.

<!-- eslint-skip -->
```ts
{
  coverage: {
    thresholds: {
      // Thresholds for all files
      functions: 95,
      branches: 70,

      // Thresholds for matching glob pattern
      'src/utils/**.ts': { 100: true },
      '**/math.ts': { 100: true }
    }
  }
}
```

## coverage.ignoreClassMethods

- **Type:** `string[]`
- **Default:** `[]`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.ignoreClassMethods=<method>`

Set to array of class method names to ignore for coverage.
See [istanbul documentation](https://github.com/istanbuljs/nyc#ignoring-methods) for more information.

## coverage.watermarks

- **Type:**
<!-- eslint-skip -->
```ts
{
  statements?: [number, number],
  functions?: [number, number],
  branches?: [number, number],
  lines?: [number, number]
}
```

- **Default:**
<!-- eslint-skip -->
```ts
{
  statements: [50, 80],
  functions: [50, 80],
  branches: [50, 80],
  lines: [50, 80]
}
```

- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.watermarks.statements=50,80`, `--coverage.watermarks.branches=50,80`

Watermarks for statements, lines, branches and functions. See [istanbul documentation](https://github.com/istanbuljs/nyc#high-and-low-watermarks) for more information.

## coverage.processingConcurrency

- **Type:** `boolean`
- **Default:** `Math.min(20, os.availableParallelism?.() ?? os.cpus().length)`
- **Available for providers:** `'v8' | 'istanbul'`
- **CLI:** `--coverage.processingConcurrency=<number>`

Concurrency limit used when processing the coverage results.

## coverage.customProviderModule

- **Type:** `string`
- **Available for providers:** `'custom'`
- **CLI:** `--coverage.customProviderModule=<path or module name>`

Specifies the module name or path for the custom coverage provider module. See [Guide - Custom Coverage Provider](/guide/coverage#custom-coverage-provider) for more information.


<!-- Source: typecheck.md -->


## typecheck <Experimental />

Options for configuring [typechecking](/guide/testing-types) test environment.

## typecheck.enabled

- **Type**: `boolean`
- **Default**: `false`
- **CLI**: `--typecheck`, `--typecheck.enabled`

Enable typechecking alongside your regular tests.

## typecheck.only

- **Type**: `boolean`
- **Default**: `false`
- **CLI**: `--typecheck.only`

Run only typecheck tests, when typechecking is enabled. When using CLI, this option will automatically enable typechecking.

## typecheck.checker

- **Type**: `'tsc' | 'vue-tsc' | string`
- **Default**: `tsc`

What tools to use for type checking. Vitest will spawn a process with certain parameters for easier parsing, depending on the type. Checker should implement the same output format as `tsc`.

You need to have a package installed to use typechecker:

- `tsc` requires `typescript` package
- `vue-tsc` requires `vue-tsc` package

You can also pass down a path to custom binary or command name that produces the same output as `tsc --noEmit --pretty false`.

## typecheck.include

- **Type**: `string[]`
- **Default**: `['**/*.{test,spec}-d.?(c|m)[jt]s?(x)']`

Glob pattern for files that should be treated as test files

## typecheck.exclude

- **Type**: `string[]`
- **Default**: `['**/node_modules/**', '**/dist/**', '**/cypress/**', '**/.{idea,git,cache,output,temp}/**']`

Glob pattern for files that should not be treated as test files

## typecheck.allowJs

- **Type**: `boolean`
- **Default**: `false`

Check JS files that have `@ts-check` comment. If you have it enabled in tsconfig, this will not overwrite it.

## typecheck.ignoreSourceErrors

- **Type**: `boolean`
- **Default**: `false`

Do not fail, if Vitest found errors outside the test files. This will not show you non-test errors at all.

By default, if Vitest finds source error, it will fail test suite.

## typecheck.tsconfig

- **Type**: `string`
- **Default**: _tries to find closest tsconfig.json_

Path to custom tsconfig, relative to the project root.

## typecheck.spawnTimeout

- **Type**: `number`
- **Default**: `10_000`

Minimum time in milliseconds it takes to spawn the typechecker.


<!-- Source: api.md -->


## api

- **Type:** `boolean | number | object`
- **Default:** `false`
- **CLI:** `--api`, `--api.port`, `--api.host`, `--api.strictPort`

Listen to port and serve API for [the UI](/guide/ui) or [browser server](/guide/browser/). When set to `true`, the default port is `51204`.

## api.allowWrite <Version>4.1.0</Version>

- **Type:** `boolean`
- **Default:** `true` if not exposed to the network, `false` otherwise

Vitest server can save test files or snapshot files via the API. This allows anyone who can connect to the API the ability to run any arbitary code on your machine.

 danger SECURITY ADVICE
Vitest does not expose the API to the internet by default and only listens on `localhost`. However if `host` is manually exposed to the network, anyone who connects to it can run arbitrary code on your machine, unless `api.allowWrite` and `api.allowExec` are set to `false`.

If the host is set to anything other than `localhost` or `127.0.0.1`, Vitest will set `api.allowWrite` and `api.allowExec` to `false` by default. This means that any write operations (like changing the code in the UI) will not work. However, if you understand the security implications, you can override them.


## api.allowExec <Version>4.1.0</Version>

- **Type:** `boolean`
- **Default:** `true` if not exposed to the network, `false` otherwise

Allows running any test file via the API. See the security advice in [`api.allowWrite`](#api-allowwrite).


<!-- Source: css.md -->


## css

- **Type**: `boolean | { include?, exclude?, modules? }`

Configure if CSS should be processed. When excluded, CSS files will be replaced with empty strings to bypass the subsequent processing. CSS Modules will return a proxy to not affect runtime.

 warning
This option is not applied to [browser tests](/guide/browser/).


## css.include

- **Type**: `RegExp | RegExp[]`
- **Default**: `[]`

RegExp pattern for files that should return actual CSS and will be processed by Vite pipeline.

> **Tip:** To process all CSS files, use `/.+/`.


## css.exclude

- **Type**: `RegExp | RegExp[]`
- **Default**: `[]`

RegExp pattern for files that will return an empty CSS file.

## css.modules

- **Type**: `{ classNameStrategy? }`
- **Default**: `{}`

### css.modules.classNameStrategy

- **Type**: `'stable' | 'scoped' | 'non-scoped'`
- **Default**: `'stable'`

If you decide to process CSS files, you can configure if class names inside CSS modules should be scoped. You can choose one of the options:

- `stable`: class names will be generated as `_${name}_${hashedFilename}`, which means that generated class will stay the same, if CSS content is changed, but will change, if the name of the file is modified, or file is moved to another folder. This setting is useful, if you use snapshot feature.
- `scoped`: class names will be generated as usual, respecting `css.modules.generateScopedName` method, if you have one and CSS processing is enabled. By default, filename will be generated as `_${name}_${hash}`, where hash includes filename and content of the file.
- `non-scoped`: class names will not be hashed.

 warning
By default, Vitest exports a proxy, bypassing CSS Modules processing. If you rely on CSS properties on your classes, you have to enable CSS processing using `include` option.



<!-- Source: isolate.md -->


## isolate

- **Type:** `boolean`
- **Default:** `true`
- **CLI:** `--no-isolate`, `--isolate=false`

Run tests in an isolated environment. This option has no effect on `vmThreads` and `vmForks` pools.

Disabling this option might [improve performance](/guide/improving-performance) if your code doesn't rely on side effects (which is usually true for projects with `node` environment).

 tip
You can disable isolation for specific test files by using Vitest workspaces and disabling isolation per project.



<!-- Source: ui.md -->


## ui <CRoot />

- **Type:** `boolean`
- **Default:** `false`
- **CLI:** `--ui`, `--ui=false`

Enable [Vitest UI](/guide/ui).

 warning
This features requires a [`@vitest/ui`](https://www.npmjs.com/package/@vitest/ui) package to be installed. If you do not have it already, Vitest will install it when you run the test command for the first time.


 danger SECURITY ADVICE
Make sure that your UI server is not exposed to the network. Since Vitest 4.1 setting [`api.host`](/config/api) to anything other than `localhost` will disable the buttons to save the code or run any tests for security reasons, effectively making UI a readonly reporter.



<!-- Source: expect.md -->


## expect

- **Type:** `ExpectOptions`

## expect.requireAssertions

- **Type:** `boolean`
- **Default:** `false`

The same as calling [`expect.hasAssertions()`](/api/expect#expect-hasassertions) at the start of every test. This makes sure that no test will pass accidentally.

 tip
This only works with Vitest's `expect`. If you use `assert` or `.should` assertions, they will not count, and your test will fail due to the lack of expect assertions.

You can change the value of this by calling `vi.setConfig({ expect: { requireAssertions: false } })`. The config will be applied to every subsequent `expect` call until the `vi.resetConfig` is called manually.


 warning
When you run tests with `sequence.concurrent` and `expect.requireAssertions` set to `true`, you should use [local expect](/guide/test-context.html#expect) instead of the global one. Otherwise, this may cause false negatives in [some situations (#8469)](https://github.com/vitest-dev/vitest/issues/8469).


## expect.poll

Global configuration options for [`expect.poll`](/api/expect#poll). These are the same options you can pass down to `expect.poll(condition, options)`.

### expect.poll.interval

- **Type:** `number`
- **Default:** `50`

Polling interval in milliseconds

### expect.poll.timeout

- **Type:** `number`
- **Default:** `1000`

Polling timeout in milliseconds


