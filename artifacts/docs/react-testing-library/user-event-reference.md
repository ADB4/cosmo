<!--
Topics: user-event, userEvent, user-event setup, click, type, keyboard, pointer, hover, tab, clear, upload, paste, fireEvent vs user-event, simulating user interactions, user simulation
Keywords: user event, simulate user, click button, type input, keyboard event, user interaction, fireEvent alternative, userEvent.click, userEvent.type
-->
# user-event Reference

<!-- Source: user-event-intro.md -->


[`user-event`](https://github.com/testing-library/user-event) is a companion
library for Testing Library that simulates user interactions by dispatching the
events that would happen if the interaction took place in a browser.

note Latest version

These docs describe `user-event@14`. We recommend updating your projects to this
version, as it includes important bug fixes and new features. You can find the
docs for `user-event@13.5.0` [here](./v13.mdx), and the
changelog for the release
[here](https://github.com/testing-library/user-event/releases/tag/v14.0.0).



While most examples with `user-event` are for `React`, the library can be used
with any framework as long as there is a DOM.

## Differences from `fireEvent`

`fireEvent` dispatches _DOM events_, whereas `user-event` simulates full
_interactions_, which may fire multiple events and do additional checks along
the way.

Testing Library's built-in
[`fireEvent`](dom-testing-library/api-events.mdx#fireevent) is a lightweight
wrapper around the browser's low-level `dispatchEvent` API, which allows
developers to trigger any event on any element. The problem is that the browser
usually does more than just trigger one event for one interaction. For example,
when a user types into a text box, the element has to be focused, and then
keyboard and input events are fired and the selection and value on the element
are manipulated as they type.

`user-event` allows you to describe a user interaction instead of a concrete
event. It adds visibility and interactability checks along the way and
manipulates the DOM just like a user interaction in the browser would. It
factors in that the browser e.g. wouldn't let a user click a hidden element or
type in a disabled text box.  
This is
[why you should use `user-event`](https://ph-fritsche.github.io/blog/post/why-userevent)
to test interaction with your components.

There are, however, some user interactions or aspects of these
[that aren't yet implemented and thus can't yet be described with `user-event`](https://github.com/testing-library/user-event/issues?q=is%3Aopen+label%3Aaccuracy%2Cenhancement).
In these cases you can use `fireEvent` to dispatch the concrete events that your
software relies on.

Note that this makes your component and/or test reliant upon your assumptions
about the concrete aspects of the interaction being correct. Therefore if you
already put in the work to specify the correct aspects of such interaction,
please consider contributing to this project so that `user-event` might cover
these cases too.

## Writing tests with `userEvent`

We recommend invoking [`userEvent.setup()`](setup.mdx) before the component is
rendered. This can be done in the test itself, or by using a setup function. We
discourage rendering or using any `userEvent` functions outside of the test
itself - e.g. in a `before`/`after` hook - for reasons described in
["Avoid Nesting When You're Testing"](https://kentcdodds.com/blog/avoid-nesting-when-youre-testing).

```js

// inlining
test('trigger some awesome feature when clicking the button', async () => {
  const user = userEvent.setup()
  // Import `render` and `screen` from the framework library of your choice.
  // See https://testing-library.com/docs/dom-testing-library/install#wrappers
  render(<MyComponent />)

  await user.click(screen.getByRole('button', {name: /click me!/i}))

  // ...assertions...
})
```

```js

// setup function
function setup(jsx) {
  return {
    user: userEvent.setup(),
    // Import `render` from the framework library of your choice.
    // See https://testing-library.com/docs/dom-testing-library/install#wrappers
    ...render(jsx),
  }
}

test('render with a setup function', async () => {
  const {user} = setup(<MyComponent />)
  // ...
})
```

Note that, while directly invoking APIs such as `userEvent.click()` (which will
trigger `setup` internally) is
[still supported in v14](https://testing-library.com/docs/user-event/setup#direct-apis),
this option exists to ease the migration from v13 to v14, and for simple tests.
We recommend using the methods on the instances returned by `userEvent.setup()`.

## Setup
<!-- Topics: user-event setup, userEvent.setup, user-event configuration, delay option -->

<!-- Source: user-event-setup.md -->


When users interact in the browser by e.g. pressing keyboard keys, they interact
with a UI layer the browser shows to them. The browser then interprets this
input, possibly alters the underlying DOM accordingly and dispatches
[trusted](https://developer.mozilla.org/en-US/docs/Web/API/Event/isTrusted)
events.  
The UI layer and trusted events are not programmatically available.  
Therefore `user-event` has to apply workarounds and mock the UI layer to
simulate user interactions like they would happen in the browser.

## Starting a session per `setup()`

```ts
setup(options?: Options): UserEvent
```

The `userEvent.setup()` API applies these workarounds to the document and allows
you to [configure](options.mdx) an "instance" of `user-event`.  
Methods on this instance share one input device state, e.g. which keys are
pressed.

This allows to write multiple consecutive interactions that behave just like the
described interactions by a real user.

```js

const user = userEvent.setup()

await user.keyboard('[ShiftLeft>]') // Press Shift (without releasing it)
await user.click(element) // Perform a click with `shiftKey: true`
```

The instance exposes another `.setup()` API that allows to configure another
instance that shares the same input device state.

The [Clipboard API](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard)
is usually not available outside of secure context.  
To enable testing of workflows involving the clipboard,
[`userEvent.setup()`](setup.mdx) replaces `window.navigator.clipboard` with a
stub.

## Direct APIs

You can also call the APIs directly on the default export. This will call
`setup` internally and then use the method on the instance.

This exists to ease the transition to version 14 and writing simple tests. Using
the methods on the instances returned by `userEvent.setup()` is recommended.
