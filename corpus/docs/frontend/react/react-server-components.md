---
title: React Server Components
source: react.dev
syllabus_weeks: [8]
topics: [Server Components, RSC, use client, use server, server functions]
---



# Server Components

Server Components are a new type of Component that renders ahead of time, before bundling, in an environment separate from your client app or SSR server.

This separate environment is the "server" in React Server Components. Server Components can run once at build time on your CI server, or they can be run for each request using a web server.

<InlineToc />

> **Note: How do I build support for Server Components? {/*how-do-i-build-support-for-server-components*/}**
>
> While React Server Components in React 19 are stable and will not break between minor versions, the underlying APIs used to implement a React Server Components bundler or framework do not follow semver and may break between minors in React 19.x.
> 
> To support React Server Components as a bundler or framework, we recommend pinning to a specific React version, or using the Canary release. We will continue working with bundlers and frameworks to stabilize the APIs used to implement React Server Components in the future.


### Server Components without a Server {/*server-components-without-a-server*/}
Server components can run at build time to read from the filesystem or fetch static content, so a web server is not required. For example, you may want to read static data from a content management system.

Without Server Components, it's common to fetch static data on the client with an Effect:
```js
// bundle.js
import marked from 'marked'; // 35.9K (11.2K gzipped)
import sanitizeHtml from 'sanitize-html'; // 206K (63.3K gzipped)

function Page({page}) {
  const [content, setContent] = useState('');
  // NOTE: loads *after* first page render.
  useEffect(() => {
    fetch(`/api/content/${page}`).then((data) => {
      setContent(data.content);
    });
  }, [page]);

  return <div>{sanitizeHtml(marked(content))}</div>;
}
```
```js
// api.js
app.get(`/api/content/:page`, async (req, res) => {
  const page = req.params.page;
  const content = await file.readFile(`${page}.md`);
  res.send({content});
});
```

This pattern means users need to download and parse an additional 75K (gzipped) of libraries, and wait for a second request to fetch the data after the page loads, just to render static content that will not change for the lifetime of the page.

With Server Components, you can render these components once at build time:

```js
import marked from 'marked'; // Not included in bundle
import sanitizeHtml from 'sanitize-html'; // Not included in bundle

async function Page({page}) {
  // NOTE: loads *during* render, when the app is built.
  const content = await file.readFile(`${page}.md`);

  return <div>{sanitizeHtml(marked(content))}</div>;
}
```

The rendered output can then be server-side rendered (SSR) to HTML and uploaded to a CDN. When the app loads, the client will not see the original `Page` component, or the expensive libraries for rendering the markdown. The client will only see the rendered output:

```js
<div><!-- html for markdown --></div>
```

This means the content is visible during first page load, and the bundle does not include the expensive libraries needed to render the static content.

> **Note:**
>
> 
> 
> You may notice that the Server Component above is an async function:
> 
> ```js
> async function Page({page}) {
>   //...
> }
> ```
> 
> Async Components are a new feature of Server Components that allow you to `await` in render.
> 
> See [Async components with Server Components](#async-components-with-server-components) below.
> 
> 


### Server Components with a Server {/*server-components-with-a-server*/}
Server Components can also run on a web server during a request for a page, letting you access your data layer without having to build an API. They are rendered before your application is bundled, and can pass data and JSX as props to Client Components.

Without Server Components, it's common to fetch dynamic data on the client in an Effect:

```js
// bundle.js
function Note({id}) {
  const [note, setNote] = useState('');
  // NOTE: loads *after* first render.
  useEffect(() => {
    fetch(`/api/notes/${id}`).then(data => {
      setNote(data.note);
    });
  }, [id]);

  return (
    <div>
      <Author id={note.authorId} />
      <p>{note}</p>
    </div>
  );
}

function Author({id}) {
  const [author, setAuthor] = useState('');
  // NOTE: loads *after* Note renders.
  // Causing an expensive client-server waterfall.
  useEffect(() => {
    fetch(`/api/authors/${id}`).then(data => {
      setAuthor(data.author);
    });
  }, [id]);

  return <span>By: {author.name}</span>;
}
```
```js
// api
import db from './database';

app.get(`/api/notes/:id`, async (req, res) => {
  const note = await db.notes.get(id);
  res.send({note});
});

app.get(`/api/authors/:id`, async (req, res) => {
  const author = await db.authors.get(id);
  res.send({author});
});
```

With Server Components, you can read the data and render it in the component:

```js
import db from './database';

async function Note({id}) {
  // NOTE: loads *during* render.
  const note = await db.notes.get(id);
  return (
    <div>
      <Author id={note.authorId} />
      <p>{note}</p>
    </div>
  );
}

async function Author({id}) {
  // NOTE: loads *after* Note,
  // but is fast if data is co-located.
  const author = await db.authors.get(id);
  return <span>By: {author.name}</span>;
}
```

The bundler then combines the data, rendered Server Components and dynamic Client Components into a bundle. Optionally, that bundle can then be server-side rendered (SSR) to create the initial HTML for the page. When the page loads, the browser does not see the original `Note` and `Author` components; only the rendered output is sent to the client:

```js
<div>
  <span>By: The React Team</span>
  <p>React 19 is...</p>
</div>
```

Server Components can be made dynamic by re-fetching them from a server, where they can access the data and render again. This new application architecture combines the simple “request/response” mental model of server-centric Multi-Page Apps with the seamless interactivity of client-centric Single-Page Apps, giving you the best of both worlds.

### Adding interactivity to Server Components {/*adding-interactivity-to-server-components*/}

Server Components are not sent to the browser, so they cannot use interactive APIs like `useState`. To add interactivity to Server Components, you can compose them with Client Component using the `"use client"` directive.

> **Note: There is no directive for Server Components. {/*there-is-no-directive-for-server-components*/}**
>
> A common misunderstanding is that Server Components are denoted by `"use server"`, but there is no directive for Server Components. The `"use server"` directive is used for Server Functions.
> 
> For more info, see the docs for [Directives](/reference/rsc/directives).



In the following example, the `Notes` Server Component imports an `Expandable` Client Component that uses state to toggle its `expanded` state:
```js
// Server Component
import Expandable from './Expandable';

async function Notes() {
  const notes = await db.notes.getAll();
  return (
    <div>
      {notes.map(note => (
        <Expandable key={note.id}>
          <p note={note} />
        </Expandable>
      ))}
    </div>
  )
}
```
```js
// Client Component
"use client"

export default function Expandable({children}) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
      >
        Toggle
      </button>
      {expanded && children}
    </div>
  )
}
```

This works by first rendering `Notes` as a Server Component, and then instructing the bundler to create a bundle for the Client Component `Expandable`. In the browser, the Client Components will see output of the Server Components passed as props:

```js
<head>
  <!-- the bundle for Client Components -->
  <script src="bundle.js" />
</head>
<body>
  <div>
    <Expandable key={1}>
      <p>this is the first note</p>
    </Expandable>
    <Expandable key={2}>
      <p>this is the second note</p>
    </Expandable>
    <!--...-->
  </div>
</body>
```

### Async components with Server Components {/*async-components-with-server-components*/}

Server Components introduce a new way to write Components using async/await. When you `await` in an async component, React will suspend and wait for the promise to resolve before resuming rendering. This works across server/client boundaries with streaming support for Suspense.

You can even create a promise on the server, and await it on the client:

```js
// Server Component
import db from './database';

async function Page({id}) {
  // Will suspend the Server Component.
  const note = await db.notes.get(id);

  // NOTE: not awaited, will start here and await on the client.
  const commentsPromise = db.comments.get(note.id);
  return (
    <div>
      {note}
      <Suspense fallback={<p>Loading Comments...</p>}>
        <Comments commentsPromise={commentsPromise} />
      </Suspense>
    </div>
  );
}
```

```js
// Client Component
"use client";
import {use} from 'react';

function Comments({commentsPromise}) {
  // NOTE: this will resume the promise from the server.
  // It will suspend until the data is available.
  const comments = use(commentsPromise);
  return comments.map(comment => <p>{comment}</p>);
}
```

The `note` content is important data for the page to render, so we `await` it on the server. The comments are below the fold and lower-priority, so we start the promise on the server, and wait for it on the client with the `use` API. This will Suspend on the client, without blocking the `note` content from rendering.

Since async components are not supported on the client, we await the promise with `use`.


# Use Client

<RSC>

`'use client'` is for use with [React Server Components](/reference/rsc/server-components).

</RSC>


`'use client'` lets you mark what code runs on the client.

<InlineToc />

---

## Reference {/*reference*/}

### `'use client'` {/*use-client*/}

Add `'use client'` at the top of a file to mark the module and its transitive dependencies as client code.

```js {1}
'use client';

import { useState } from 'react';
import { formatDate } from './formatters';
import Button from './button';

export default function RichTextEditor({ timestamp, text }) {
  const date = formatDate(timestamp);
  // ...
  const editButton = <Button />;
  // ...
}
```

When a file marked with `'use client'` is imported from a Server Component, [compatible bundlers](/learn/creating-a-react-app#full-stack-frameworks) will treat the module import as a boundary between server-run and client-run code.

As dependencies of `RichTextEditor`, `formatDate` and `Button` will also be evaluated on the client regardless of whether their modules contain a `'use client'` directive. Note that a single module may be evaluated on the server when imported from server code and on the client when imported from client code.

#### Caveats {/*caveats*/}

* `'use client'` must be at the very beginning of a file, above any imports or other code (comments are OK). They must be written with single or double quotes, but not backticks.
* When a `'use client'` module is imported from another client-rendered module, the directive has no effect.
* When a component module contains a `'use client'` directive, any usage of that component is guaranteed to be a Client Component. However, a component can still be evaluated on the client even if it does not have a `'use client'` directive.
	* A component usage is considered a Client Component if it is defined in module with `'use client'` directive or when it is a transitive dependency of a module that contains a `'use client'` directive. Otherwise, it is a Server Component.
* Code that is marked for client evaluation is not limited to components. All code that is a part of the Client module sub-tree is sent to and run by the client.
* When a server evaluated module imports values from a `'use client'` module, the values must either be a React component or [supported serializable prop values](#passing-props-from-server-to-client-components) to be passed to a Client Component. Any other use case will throw an exception.

### How `'use client'` marks client code {/*how-use-client-marks-client-code*/}

In a React app, components are often split into separate files, or [modules](/learn/importing-and-exporting-components#exporting-and-importing-a-component).

For apps that use React Server Components, the app is server-rendered by default. `'use client'` introduces a server-client boundary in the [module dependency tree](/learn/understanding-your-ui-as-a-tree#the-module-dependency-tree), effectively creating a subtree of Client modules.

To better illustrate this, consider the following React Server Components app.

[Interactive example removed — see react.dev for live demo]


In the module dependency tree of this example app, the `'use client'` directive in `InspirationGenerator.js` marks that module and all of its transitive dependencies as Client modules. The subtree starting at `InspirationGenerator.js` is now marked as Client modules.

<Diagram name="use_client_module_dependency" height={250} width={545} alt="A tree graph with the top node representing the module 'App.js'. 'App.js' has three children: 'Copyright.js', 'FancyText.js', and 'InspirationGenerator.js'. 'InspirationGenerator.js' has two children: 'FancyText.js' and 'inspirations.js'. The nodes under and including 'InspirationGenerator.js' have a yellow background color to signify that this sub-graph is client-rendered due to the 'use client' directive in 'InspirationGenerator.js'.">
`'use client'` segments the module dependency tree of the React Server Components app, marking `InspirationGenerator.js` and all of its dependencies as client-rendered.
</Diagram>

During render, the framework will server-render the root component and continue through the [render tree](/learn/understanding-your-ui-as-a-tree#the-render-tree), opting-out of evaluating any code imported from client-marked code.

The server-rendered portion of the render tree is then sent to the client. The client, with its client code downloaded, then completes rendering the rest of the tree.

<Diagram name="use_client_render_tree" height={250} width={500} alt="A tree graph where each node represents a component and its children as child components. The top-level node is labelled 'App' and it has two child components 'InspirationGenerator' and 'FancyText'. 'InspirationGenerator' has two child components, 'FancyText' and 'Copyright'. Both 'InspirationGenerator' and its child component 'FancyText' are marked to be client-rendered.">
The render tree for the React Server Components app. `InspirationGenerator` and its child component `FancyText` are components exported from client-marked code and considered Client Components.
</Diagram>

We introduce the following definitions:

* **Client Components** are components in a render tree that are rendered on the client.
* **Server Components** are components in a render tree that are rendered on the server.

Working through the example app, `App`, `FancyText` and `Copyright` are all server-rendered and considered Server Components. As `InspirationGenerator.js` and its transitive dependencies are marked as client code, the component `InspirationGenerator` and its child component `FancyText` are Client Components.

> **Deep Dive: How is `FancyText` both a Server and a Client Component? {/*how-is-fancytext-both-a-server-and-a-client-component*/}**
>
> By the above definitions, the component `FancyText` is both a Server and Client Component, how can that be?
> 
> First, let's clarify that the term "component" is not very precise. Here are just two ways "component" can be understood:
> 
> 1. A "component" can refer to a **component definition**. In most cases this will be a function.
> 
> ```js
> // This is a definition of a component
> function MyComponent() {
>   return <p>My Component</p>
> }
> ```
> 
> 2. A "component" can also refer to a **component usage** of its definition.
> ```js
> import MyComponent from './MyComponent';
> 
> function App() {
>   // This is a usage of a component
>   return <MyComponent />;
> }
> ```
> 
> Often, the imprecision is not important when explaining concepts, but in this case it is.
> 
> When we talk about Server or Client Components, we are referring to component usages.
> 
> * If the component is defined in a module with a `'use client'` directive, or the component is imported and called in a Client Component, then the component usage is a Client Component.
> * Otherwise, the component usage is a Server Component.
> 
> 
> <Diagram name="use_client_render_tree" height={150} width={450} alt="A tree graph where each node represents a component and its children as child components. The top-level node is labelled 'App' and it has two child components 'InspirationGenerator' and 'FancyText'. 'InspirationGenerator' has two child components, 'FancyText' and 'Copyright'. Both 'InspirationGenerator' and its child component 'FancyText' are marked to be client-rendered.">A render tree illustrates component usages.</Diagram>
> 
> Back to the question of `FancyText`, we see that the component definition does _not_ have a `'use client'` directive and it has two usages.
> 
> The usage of `FancyText` as a child of `App`, marks that usage as a Server Component. When `FancyText` is imported and called under `InspirationGenerator`, that usage of `FancyText` is a Client Component as `InspirationGenerator` contains a `'use client'` directive.
> 
> This means that the component definition for `FancyText` will both be evaluated on the server and also downloaded by the client to render its Client Component usage.


> **Deep Dive: Why is `Copyright` a Server Component? {/*why-is-copyright-a-server-component*/}**
>
> Because `Copyright` is rendered as a child of the Client Component `InspirationGenerator`, you might be surprised that it is a Server Component.
> 
> Recall that `'use client'` defines the boundary between server and client code on the _module dependency tree_, not the render tree.
> 
> <Diagram name="use_client_module_dependency" height={200} width={500} alt="A tree graph with the top node representing the module 'App.js'. 'App.js' has three children: 'Copyright.js', 'FancyText.js', and 'InspirationGenerator.js'. 'InspirationGenerator.js' has two children: 'FancyText.js' and 'inspirations.js'. The nodes under and including 'InspirationGenerator.js' have a yellow background color to signify that this sub-graph is client-rendered due to the 'use client' directive in 'InspirationGenerator.js'.">
> `'use client'` defines the boundary between server and client code on the module dependency tree.
> </Diagram>
> 
> In the module dependency tree, we see that `App.js` imports and calls `Copyright` from the `Copyright.js` module. As `Copyright.js` does not contain a `'use client'` directive, the component usage is rendered on the server. `App` is rendered on the server as it is the root component.
> 
> Client Components can render Server Components because you can pass JSX as props. In this case, `InspirationGenerator` receives `Copyright` as [children](/learn/passing-props-to-a-component#passing-jsx-as-children). However, the `InspirationGenerator` module never directly imports the `Copyright` module nor calls the component, all of that is done by `App`. In fact, the `Copyright` component is fully executed before `InspirationGenerator` starts rendering.
> 
> The takeaway is that a parent-child render relationship between components does not guarantee the same render environment.


### When to use `'use client'` {/*when-to-use-use-client*/}

With `'use client'`, you can determine when components are Client Components. As Server Components are default, here is a brief overview of the advantages and limitations to Server Components to determine when you need to mark something as client rendered.

For simplicity, we talk about Server Components, but the same principles apply to all code in your app that is server run.

#### Advantages of Server Components {/*advantages*/}
* Server Components can reduce the amount of code sent and run by the client. Only Client modules are bundled and evaluated by the client.
* Server Components benefit from running on the server. They can access the local filesystem and may experience low latency for data fetches and network requests.

#### Limitations of Server Components {/*limitations*/}
* Server Components cannot support interaction as event handlers must be registered and triggered by a client.
	* For example, event handlers like `onClick` can only be defined in Client Components.
* Server Components cannot use most Hooks.
	* When Server Components are rendered, their output is essentially a list of components for the client to render. Server Components do not persist in memory after render and cannot have their own state.

### Serializable types returned by Server Components {/*serializable-types*/}

As in any React app, parent components pass data to child components. As they are rendered in different environments, passing data from a Server Component to a Client Component requires extra consideration.

Prop values passed from a Server Component to Client Component must be serializable.

Serializable props include:
* Primitives
	* [string](https://developer.mozilla.org/en-US/docs/Glossary/String)
	* [number](https://developer.mozilla.org/en-US/docs/Glossary/Number)
	* [bigint](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt)
	* [boolean](https://developer.mozilla.org/en-US/docs/Glossary/Boolean)
	* [undefined](https://developer.mozilla.org/en-US/docs/Glossary/Undefined)
	* [null](https://developer.mozilla.org/en-US/docs/Glossary/Null)
	* [symbol](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol), only symbols registered in the global Symbol registry via [`Symbol.for`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol/for)
* Iterables containing serializable values
	* [String](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)
	* [Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
	* [Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
	* [Set](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set)
	* [TypedArray](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray) and [ArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer)
* [Date](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
* Plain [objects](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object): those created with [object initializers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Object_initializer), with serializable properties
* Functions that are [Server Functions](/reference/rsc/server-functions)
* Client or Server Component elements (JSX)
* [Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)

Notably, these are not supported:
* [Functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Function) that are not exported from client-marked modules or marked with [`'use server'`](/reference/rsc/use-server)
* [Classes](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/Classes_in_JavaScript)
* Objects that are instances of any class (other than the built-ins mentioned) or objects with [a null prototype](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object#null-prototype_objects)
* Symbols not registered globally, ex. `Symbol('my new symbol')`


## Usage {/*usage*/}

### Building with interactivity and state {/*building-with-interactivity-and-state*/}

[Interactive example removed — see react.dev for live demo]


As `Counter` requires both the `useState` Hook and event handlers to increment or decrement the value, this component must be a Client Component and will require a `'use client'` directive at the top.

In contrast, a component that renders UI without interaction will not need to be a Client Component.

```js
import { readFile } from 'node:fs/promises';
import Counter from './Counter';

export default async function CounterContainer() {
  const initialValue = await readFile('/path/to/counter_value');
  return <Counter initialValue={initialValue} />
}
```

For example, `Counter`'s parent component, `CounterContainer`, does not require `'use client'` as it is not interactive and does not use state. In addition, `CounterContainer` must be a Server Component as it reads from the local file system on the server, which is possible only in a Server Component.

There are also components that don't use any server or client-only features and can be agnostic to where they render. In our earlier example, `FancyText` is one such component.

```js
export default function FancyText({title, text}) {
  return title
    ? <h1 className='fancy title'>{text}</h1>
    : <h3 className='fancy cursive'>{text}</h3>
}
```

In this case, we don't add the `'use client'` directive, resulting in `FancyText`'s _output_ (rather than its source code) to be sent to the browser when referenced from a Server Component. As demonstrated in the earlier Inspirations app example, `FancyText` is used as both a Server or Client Component, depending on where it is imported and used.

But if `FancyText`'s HTML output was large relative to its source code (including dependencies), it might be more efficient to force it to always be a Client Component. Components that return a long SVG path string are one case where it may be more efficient to force a component to be a Client Component.

### Using client APIs {/*using-client-apis*/}

Your React app may use client-specific APIs, such as the browser's APIs for web storage, audio and video manipulation, and device hardware, among [others](https://developer.mozilla.org/en-US/docs/Web/API).

In this example, the component uses [DOM APIs](https://developer.mozilla.org/en-US/docs/Glossary/DOM) to manipulate a [`canvas`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/canvas) element. Since those APIs are only available in the browser, it must be marked as a Client Component.

```js
'use client';

import {useRef, useEffect} from 'react';

export default function Circle() {
  const ref = useRef(null);
  useLayoutEffect(() => {
    const canvas = ref.current;
    const context = canvas.getContext('2d');
    context.reset();
    context.beginPath();
    context.arc(100, 75, 50, 0, 2 * Math.PI);
    context.stroke();
  });
  return <canvas ref={ref} />;
}
```

### Using third-party libraries {/*using-third-party-libraries*/}

Often in a React app, you'll leverage third-party libraries to handle common UI patterns or logic.

These libraries may rely on component Hooks or client APIs. Third-party components that use any of the following React APIs must run on the client:
* [createContext](/reference/react/createContext)
* [`react`](/reference/react/hooks) and [`react-dom`](/reference/react-dom/hooks) Hooks, excluding [`use`](/reference/react/use) and [`useId`](/reference/react/useId)
* [forwardRef](/reference/react/forwardRef)
* [memo](/reference/react/memo)
* [startTransition](/reference/react/startTransition)
* If they use client APIs, ex. DOM insertion or native platform views

If these libraries have been updated to be compatible with React Server Components, then they will already include `'use client'` markers of their own, allowing you to use them directly from your Server Components. If a library hasn't been updated, or if a component needs props like event handlers that can only be specified on the client, you may need to add your own Client Component file in between the third-party Client Component and your Server Component where you'd like to use it.

[TODO]: <> (Troubleshooting - need use-cases)


# Use Server

<RSC>

`'use server'` is for use with [using React Server Components](/reference/rsc/server-components).

</RSC>


`'use server'` marks server-side functions that can be called from client-side code.

<InlineToc />

---

## Reference {/*reference*/}

### `'use server'` {/*use-server*/}

Add `'use server'` at the top of an async function body to mark the function as callable by the client. We call these functions [_Server Functions_](/reference/rsc/server-functions).

```js {2}
async function addToCart(data) {
  'use server';
  // ...
}
```

When calling a Server Function on the client, it will make a network request to the server that includes a serialized copy of any arguments passed. If the Server Function returns a value, that value will be serialized and returned to the client.

Instead of individually marking functions with `'use server'`, you can add the directive to the top of a file to mark all exports within that file as Server Functions that can be used anywhere, including imported in client code.

#### Caveats {/*caveats*/}
* `'use server'` must be at the very beginning of their function or module; above any other code including imports (comments above directives are OK). They must be written with single or double quotes, not backticks.
* `'use server'` can only be used in server-side files. The resulting Server Functions can be passed to Client Components through props. See supported [types for serialization](#serializable-parameters-and-return-values).
* To import a Server Functions from [client code](/reference/rsc/use-client), the directive must be used on a module level.
* Because the underlying network calls are always asynchronous, `'use server'` can only be used on async functions.
* Always treat arguments to Server Functions as untrusted input and authorize any mutations. See [security considerations](#security).
* Server Functions should be called in a [Transition](/reference/react/useTransition). Server Functions passed to [`<form action>`](/reference/react-dom/components/form#props) or [`formAction`](/reference/react-dom/components/input#props) will automatically be called in a transition.
* Server Functions are designed for mutations that update server-side state; they are not recommended for data fetching. Accordingly, frameworks implementing Server Functions typically process one action at a time and do not have a way to cache the return value.

### Security considerations {/*security*/}

Arguments to Server Functions are fully client-controlled. For security, always treat them as untrusted input, and make sure to validate and escape arguments as appropriate.

In any Server Function, make sure to validate that the logged-in user is allowed to perform that action.

<Wip>

To prevent sending sensitive data from a Server Function, there are experimental taint APIs to prevent unique values and objects from being passed to client code.

See [experimental_taintUniqueValue](/reference/react/experimental_taintUniqueValue) and [experimental_taintObjectReference](/reference/react/experimental_taintObjectReference).

</Wip>

### Serializable arguments and return values {/*serializable-parameters-and-return-values*/}

Since client code calls the Server Function over the network, any arguments passed will need to be serializable.

Here are supported types for Server Function arguments:

* Primitives
	* [string](https://developer.mozilla.org/en-US/docs/Glossary/String)
	* [number](https://developer.mozilla.org/en-US/docs/Glossary/Number)
	* [bigint](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt)
	* [boolean](https://developer.mozilla.org/en-US/docs/Glossary/Boolean)
	* [undefined](https://developer.mozilla.org/en-US/docs/Glossary/Undefined)
	* [null](https://developer.mozilla.org/en-US/docs/Glossary/Null)
	* [symbol](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol), only symbols registered in the global Symbol registry via [`Symbol.for`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Symbol/for)
* Iterables containing serializable values
	* [String](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)
	* [Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
	* [Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
	* [Set](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set)
	* [TypedArray](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray) and [ArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer)
* [Date](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
* [FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData) instances
* Plain [objects](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object): those created with [object initializers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Object_initializer), with serializable properties
* Functions that are Server Functions
* [Promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)

Notably, these are not supported:
* React elements, or [JSX](/learn/writing-markup-with-jsx)
* Functions, including component functions or any other function that is not a Server Function
* [Classes](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/Classes_in_JavaScript)
* Objects that are instances of any class (other than the built-ins mentioned) or objects with [a null prototype](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object#null-prototype_objects)
* Symbols not registered globally, ex. `Symbol('my new symbol')`
* Events from event handlers


Supported serializable return values are the same as [serializable props](/reference/rsc/use-client#serializable-types) for a boundary Client Component.


## Usage {/*usage*/}

### Server Functions in forms {/*server-functions-in-forms*/}

The most common use case of Server Functions will be calling functions that mutate data. On the browser, the [HTML form element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/form) is the traditional approach for a user to submit a mutation. With React Server Components, React introduces first-class support for Server Functions as Actions in [forms](/reference/react-dom/components/form).

Here is a form that allows a user to request a username.

```js [[1, 3, "formData"]]
// App.js

async function requestUsername(formData) {
  'use server';
  const username = formData.get('username');
  // ...
}

export default function App() {
  return (
    <form action={requestUsername}>
      <input type="text" name="username" />
      <button type="submit">Request</button>
    </form>
  );
}
```

In this example `requestUsername` is a Server Function passed to a `<form>`. When a user submits this form, there is a network request to the server function `requestUsername`. When calling a Server Function in a form, React will supply the form's [FormData](https://developer.mozilla.org/en-US/docs/Web/API/FormData) as the first argument to the Server Function.

By passing a Server Function to the form `action`, React can [progressively enhance](https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement) the form. This means that forms can be submitted before the JavaScript bundle is loaded.

#### Handling return values in forms {/*handling-return-values*/}

In the username request form, there might be the chance that a username is not available. `requestUsername` should tell us if it fails or not.

To update the UI based on the result of a Server Function while supporting progressive enhancement, use [`useActionState`](/reference/react/useActionState).

```js
// requestUsername.js
'use server';

export default async function requestUsername(formData) {
  const username = formData.get('username');
  if (canRequest(username)) {
    // ...
    return 'successful';
  }
  return 'failed';
}
```

```js {4,8}, [[2, 2, "'use client'"]]
// UsernameForm.js
'use client';

import { useActionState } from 'react';
import requestUsername from './requestUsername';

function UsernameForm() {
  const [state, action] = useActionState(requestUsername, null, 'n/a');

  return (
    <>
      <form action={action}>
        <input type="text" name="username" />
        <button type="submit">Request</button>
      </form>
      <p>Last submission request returned: {state}</p>
    </>
  );
}
```

Note that like most Hooks, `useActionState` can only be called in [client code](/reference/rsc/use-client).

### Calling a Server Function outside of `<form>` {/*calling-a-server-function-outside-of-form*/}

Server Functions are exposed server endpoints and can be called anywhere in client code.

When using a Server Function outside a [form](/reference/react-dom/components/form), call the Server Function in a [Transition](/reference/react/useTransition), which allows you to display a loading indicator, show [optimistic state updates](/reference/react/useOptimistic), and handle unexpected errors. Forms will automatically wrap Server Functions in transitions.

```js {9-12}
import incrementLike from './actions';
import { useState, useTransition } from 'react';

function LikeButton() {
  const [isPending, startTransition] = useTransition();
  const [likeCount, setLikeCount] = useState(0);

  const onClick = () => {
    startTransition(async () => {
      const currentCount = await incrementLike();
      setLikeCount(currentCount);
    });
  };

  return (
    <>
      <p>Total Likes: {likeCount}</p>
      <button onClick={onClick} disabled={isPending}>Like</button>;
    </>
  );
}
```

```js
// actions.js
'use server';

let likeCount = 0;
export default async function incrementLike() {
  likeCount++;
  return likeCount;
}
```

To read a Server Function return value, you'll need to `await` the promise returned.


# Server Functions

<RSC>

Server Functions are for use in [React Server Components](/reference/rsc/server-components).

**Note:** Until September 2024, we referred to all Server Functions as "Server Actions". If a Server Function is passed to an action prop or called from inside an action then it is a Server Action, but not all Server Functions are Server Actions. The naming in this documentation has been updated to reflect that Server Functions can be used for multiple purposes.

</RSC>

Server Functions allow Client Components to call async functions executed on the server.

<InlineToc />

> **Note: How do I build support for Server Functions? {/*how-do-i-build-support-for-server-functions*/}**
>
> While Server Functions in React 19 are stable and will not break between minor versions, the underlying APIs used to implement Server Functions in a React Server Components bundler or framework do not follow semver and may break between minors in React 19.x. 
> 
> To support Server Functions as a bundler or framework, we recommend pinning to a specific React version, or using the Canary release. We will continue working with bundlers and frameworks to stabilize the APIs used to implement Server Functions in the future.


When a Server Function is defined with the [`"use server"`](/reference/rsc/use-server) directive, your framework will automatically create a reference to the Server Function, and pass that reference to the Client Component. When that function is called on the client, React will send a request to the server to execute the function, and return the result.

Server Functions can be created in Server Components and passed as props to Client Components, or they can be imported and used in Client Components.

## Usage {/*usage*/}

### Creating a Server Function from a Server Component {/*creating-a-server-function-from-a-server-component*/}

Server Components can define Server Functions with the `"use server"` directive:

```js [[2, 7, "'use server'"], [1, 5, "createNoteAction"], [1, 12, "createNoteAction"]]
// Server Component
import Button from './Button';

function EmptyNote () {
  async function createNoteAction() {
    // Server Function
    'use server';
    
    await db.notes.create();
  }

  return <Button onClick={createNoteAction}/>;
}
```

When React renders the `EmptyNote` Server Component, it will create a reference to the `createNoteAction` function, and pass that reference to the `Button` Client Component. When the button is clicked, React will send a request to the server to execute the `createNoteAction` function with the reference provided:

```js {5}
"use client";

export default function Button({onClick}) { 
  console.log(onClick); 
  // {$$typeof: Symbol.for("react.server.reference"), $$id: 'createNoteAction'}
  return <button onClick={() => onClick()}>Create Empty Note</button>
}
```

For more, see the docs for [`"use server"`](/reference/rsc/use-server).


### Importing Server Functions from Client Components {/*importing-server-functions-from-client-components*/}

Client Components can import Server Functions from files that use the `"use server"` directive:

```js [[1, 3, "createNote"]]
"use server";

export async function createNote() {
  await db.notes.create();
}

```

When the bundler builds the `EmptyNote` Client Component, it will create a reference to the `createNote` function in the bundle. When the `button` is clicked, React will send a request to the server to execute the `createNote` function using the reference provided:

```js [[1, 2, "createNote"], [1, 5, "createNote"], [1, 7, "createNote"]]
"use client";
import {createNote} from './actions';

function EmptyNote() {
  console.log(createNote);
  // {$$typeof: Symbol.for("react.server.reference"), $$id: 'createNote'}
  <button onClick={() => createNote()} />
}
```

For more, see the docs for [`"use server"`](/reference/rsc/use-server).

### Server Functions with Actions {/*server-functions-with-actions*/}

Server Functions can be called from Actions on the client:

```js [[1, 3, "updateName"]]
"use server";

export async function updateName(name) {
  if (!name) {
    return {error: 'Name is required'};
  }
  await db.users.updateName(name);
}
```

```js [[1, 3, "updateName"], [1, 13, "updateName"], [2, 11, "submitAction"],  [2, 23, "submitAction"]]
"use client";

import {updateName} from './actions';

function UpdateName() {
  const [name, setName] = useState('');
  const [error, setError] = useState(null);

  const [isPending, startTransition] = useTransition();

  const submitAction = async () => {
    startTransition(async () => {
      const {error} = await updateName(name);
      if (error) {
        setError(error);
      } else {
        setName('');
      }
    })
  }
  
  return (
    <form action={submitAction}>
      <input type="text" name="name" disabled={isPending}/>
      {error && <span>Failed: {error}</span>}
    </form>
  )
}
```

This allows you to access the `isPending` state of the Server Function by wrapping it in an Action on the client.

For more, see the docs for [Calling a Server Function outside of `<form>`](/reference/rsc/use-server#calling-a-server-function-outside-of-form)

### Server Functions with Form Actions {/*using-server-functions-with-form-actions*/}

Server Functions work with the new Form features in React 19.

You can pass a Server Function to a Form to automatically submit the form to the server:


```js [[1, 3, "updateName"], [1, 7, "updateName"]]
"use client";

import {updateName} from './actions';

function UpdateName() {
  return (
    <form action={updateName}>
      <input type="text" name="name" />
    </form>
  )
}
```

When the Form submission succeeds, React will automatically reset the form. You can add `useActionState` to access the pending state, last response, or to support progressive enhancement.

For more, see the docs for [Server Functions in Forms](/reference/rsc/use-server#server-functions-in-forms).

### Server Functions with `useActionState` {/*server-functions-with-use-action-state*/}

You can call Server Functions with `useActionState` for the common case where you just need access to the action pending state and last returned response:

```js [[1, 3, "updateName"], [1, 6, "updateName"], [2, 6, "submitAction"], [2, 9, "submitAction"]]
"use client";

import {updateName} from './actions';

function UpdateName() {
  const [state, submitAction, isPending] = useActionState(updateName, {error: null});

  return (
    <form action={submitAction}>
      <input type="text" name="name" disabled={isPending}/>
      {state.error && <span>Failed: {state.error}</span>}
    </form>
  );
}
```

When using `useActionState` with Server Functions, React will also automatically replay form submissions entered before hydration finishes. This means users can interact with your app even before the app has hydrated.

For more, see the docs for [`useActionState`](/reference/react/useActionState).

### Progressive enhancement with `useActionState` {/*progressive-enhancement-with-useactionstate*/}

Server Functions also support progressive enhancement with the third argument of `useActionState`.

```js [[1, 3, "updateName"], [1, 6, "updateName"], [2, 6, "/name/update"], [3, 6, "submitAction"], [3, 9, "submitAction"]]
"use client";

import {updateName} from './actions';

function UpdateName() {
  const [, submitAction] = useActionState(updateName, null, `/name/update`);

  return (
    <form action={submitAction}>
      ...
    </form>
  );
}
```

When the permalink is provided to `useActionState`, React will redirect to the provided URL if the form is submitted before the JavaScript bundle loads.

For more, see the docs for [`useActionState`](/reference/react/useActionState).
