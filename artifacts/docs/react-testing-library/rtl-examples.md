<!--
Topics: React Testing Library examples, testing input events, testing React context, testing useReducer, testing React Router, testing transitions, testing animations, updating props, integration tests
Keywords: rtl examples, test input, test context, test router, test hooks, test reducer, update props in test, integration test example
-->
# React Testing Library — Examples

## Input Event
<!-- Topics: test input events, input testing, onChange, form input testing -->

<!-- Source: example-input-event.md -->

sidebar_label: Input Event

> **Note**
>
> If you want to simulate a more natural typing behaviour while testing your
> component, consider the companion library [`user-event`](user-event/intro.mdx)

```jsx

function CostInput() {
  const [value, setValue] = useState('')

  const removeDollarSign = value => (value[0] === '$' ? value.slice(1) : value)
  const getReturnValue = value => (value === '' ? '' : `$${value}`)

  const handleChange = ev => {
    ev.preventDefault()
    const inputtedValue = ev.currentTarget.value
    const noDollarSign = removeDollarSign(inputtedValue)
    if (isNaN(noDollarSign)) return
    setValue(getReturnValue(noDollarSign))
  }

  return <input value={value} aria-label="cost-input" onChange={handleChange} />
}

const setup = () => {
  const utils = render(<CostInput />)
  const input = screen.getByLabelText('cost-input')
  return {
    input,
    ...utils,
  }
}

test('It should keep a $ in front of the input', () => {
  const {input} = setup()
  fireEvent.change(input, {target: {value: '23'}})
  expect(input.value).toBe('$23')
})
test('It should allow a $ to be in the input when the value is changed', () => {
  const {input} = setup()
  fireEvent.change(input, {target: {value: '$23.0'}})
  expect(input.value).toBe('$23.0')
})

test('It should not allow letters to be inputted', () => {
  const {input} = setup()
  expect(input.value).toBe('') // empty before
  fireEvent.change(input, {target: {value: 'Good Day'}})
  expect(input.value).toBe('') //empty after
})

test('It should allow the $ to be deleted', () => {
  const {input} = setup()
  fireEvent.change(input, {target: {value: '23'}})
  expect(input.value).toBe('$23') // need to make a change so React registers "" as a change
  fireEvent.change(input, {target: {value: ''}})
  expect(input.value).toBe('')
})
```

## React Context
<!-- Topics: test React context, context testing, context provider, useContext testing -->

<!-- Source: example-react-context.md -->


```jsx
import '@testing-library/jest-dom'

/**
 * Test default values by rendering a context consumer without a
 * matching provider
 */
test('NameConsumer shows default value', () => {
  render(<NameConsumer />)
  expect(screen.getByText(/^My Name Is:/)).toHaveTextContent(
    'My Name Is: Unknown',
  )
})

/**
 * A custom render to setup providers. Extends regular
 * render options with `providerProps` to allow injecting
 * different scenarios to test with.
 *
 * @see https://testing-library.com/docs/react-testing-library/setup#custom-render
 */
const customRender = (ui, {providerProps, ...renderOptions}) => {
  return render(
    <NameContext.Provider {...providerProps}>{ui}</NameContext.Provider>,
    renderOptions,
  )
}

test('NameConsumer shows value from provider', () => {
  const providerProps = {
    value: 'C3PO',
  }
  customRender(<NameConsumer />, {providerProps})
  expect(screen.getByText(/^My Name Is:/)).toHaveTextContent('My Name Is: C3P0')
})

/**
 * To test a component that provides a context value, render a matching
 * consumer as the child
 */
test('NameProvider composes full name from first, last', () => {
  const providerProps = {
    first: 'Boba',
    last: 'Fett',
  }
  customRender(
    <NameContext.Consumer>
      {value => <span>Received: {value}</span>}
    </NameContext.Consumer>,
    {providerProps},
  )
  expect(screen.getByText(/^Received:/).textContent).toBe('Received: Boba Fett')
})

/**
 * A tree containing both a providers and consumer can be rendered normally
 */
test('NameProvider/Consumer shows name of character', () => {
  const wrapper = ({children}) => (
    <NameProvider first="Leia" last="Organa">
      {children}
    </NameProvider>
  )

  render(<NameConsumer />, {wrapper})
  expect(screen.getByText(/^My Name Is:/).textContent).toBe(
    'My Name Is: Leia Organa',
  )
})
```

## Hooks (useReducer)
<!-- Topics: test useReducer, reducer testing, dispatch testing, state management testing -->

<!-- Source: example-react-hooks-useReducer.md -->


Basic example showing how to test the `useReducer` hook. The most important
thing is that we aren't testing the reducer directly - it's an implementation
detail of the component! Instead we are testing the component interface.

The component we are testing changes some text depending on an `isConfirmed`
state.

```jsx
// example.js


const initialState = {
  isConfirmed: false,
}

function reducer(state = initialState, action) {
  switch (action.type) {
    case 'SUCCESS':
      return {
        ...state,
        isConfirmed: true,
      }
    default:
      throw Error('unknown action')
  }
}

const Example = () => {
  const [state, dispatch] = useReducer(reducer, initialState)

  return (
    <div>
      <div>
        {state.isConfirmed ? (
          <p>Confirmed!</p>
        ) : (
          <p>Waiting for confirmation...</p>
        )}
      </div>
      <button onClick={() => dispatch({type: 'SUCCESS'})}>Confirm</button>
    </div>
  )
}

export default Example
```

We are testing to see if we get the correct output in our JSX based on the
reducer state.

```jsx
// example.test.js


it('shows success message after confirm button is clicked', () => {
  const {getByText} = render(<Example />)

  expect(getByText(/waiting/i)).toBeInTheDocument()

  fireEvent.click(getByText('Confirm'))

  expect(getByText('Confirmed!')).toBeInTheDocument()
})
```

## React Router
<!-- Topics: test React Router, router testing, navigation testing, route testing -->

<!-- Source: example-react-router.md -->


This example demonstrates React Router v6. For previous versions see below.

```jsx
// app.js

const About = () => <div>You are on the about page</div>
const Home = () => <div>You are home</div>
const NoMatch = () => <div>No match</div>

export const LocationDisplay = () => {
  const location = useLocation()

  return <div data-testid="location-display">{location.pathname}</div>
}

export const App = () => (
  <div>
    <Link to="/">Home</Link>

    <Link to="/about">About</Link>

    <Routes>
      <Route path="/" element={<Home />} />

      <Route path="/about" element={<About />} />

      <Route path="*" element={<NoMatch />} />
    </Routes>

    <LocationDisplay />
  </div>
)
```

```jsx
// app.test.js
import '@testing-library/jest-dom'

test('full app rendering/navigating', async () => {
  render(<App />, {wrapper: BrowserRouter})
  const user = userEvent.setup()

  // verify page content for default route
  expect(screen.getByText(/you are home/i)).toBeInTheDocument()

  // verify page content for expected route after navigating
  await user.click(screen.getByText(/about/i))
  expect(screen.getByText(/you are on the about page/i)).toBeInTheDocument()
})

test('landing on a bad page', () => {
  const badRoute = '/some/bad/route'

  // use <MemoryRouter> when you want to manually control the history
  render(
    <MemoryRouter initialEntries={[badRoute]}>
      <App />
    </MemoryRouter>,
  )

  // verify navigation to "no match" route
  expect(screen.getByText(/no match/i)).toBeInTheDocument()
})

test('rendering a component that uses useLocation', () => {
  const route = '/some-route'

  // use <MemoryRouter> when you want to manually control the history
  render(
    <MemoryRouter initialEntries={[route]}>
      <LocationDisplay />
    </MemoryRouter>,
  )

  // verify location display is rendered
  expect(screen.getByTestId('location-display')).toHaveTextContent(route)
})
```

## Reducing boilerplate

1. If you find yourself adding Router components to your tests a lot, you may
   want to create a helper function that wraps around `render`.

```jsx
// test utils file
const renderWithRouter = (ui, {route = '/'} = {}) => {
  window.history.pushState({}, 'Test page', route)

  return {
    user: userEvent.setup(),
    ...render(ui, {wrapper: BrowserRouter}),
  }
}
```

```jsx
// app.test.js
test('full app rendering/navigating', async () => {
  const {user} = renderWithRouter(<App />)
  expect(screen.getByText(/you are home/i)).toBeInTheDocument()

  await user.click(screen.getByText(/about/i))

  expect(screen.getByText(/you are on the about page/i)).toBeInTheDocument()
})

test('landing on a bad page', () => {
  renderWithRouter(<App />, {route: '/something-that-does-not-match'})

  expect(screen.getByText(/no match/i)).toBeInTheDocument()
})

test('rendering a component that uses useLocation', () => {
  const route = '/some-route'
  renderWithRouter(<LocationDisplay />, {route})

  expect(screen.getByTestId('location-display')).toHaveTextContent(route)
})
```

## Testing Library and React Router v5

```jsx
// app.js

const About = () => <div>You are on the about page</div>
const Home = () => <div>You are home</div>
const NoMatch = () => <div>No match</div>

export const LocationDisplay = () => {
  const location = useLocation()

  return <div data-testid="location-display">{location.pathname}</div>
}

export const App = () => (
  <div>
    <Link to="/">Home</Link>

    <Link to="/about">About</Link>

    <Switch>
      <Route exact path="/" component={Home} />

      <Route path="/about" component={About} />

      <Route component={NoMatch} />
    </Switch>

    <LocationDisplay />
  </div>
)
```

In your tests, pass the history object as a whole to the Router component.
**Note:** React Router v5
[only works with History v4](https://github.com/remix-run/history#documentation),
so make sure you have the correct version of `history` installed.

```jsx
// app.test.js
import '@testing-library/jest-dom'

// React Router v5

test('full app rendering/navigating', async () => {
  const history = createMemoryHistory()
  render(
    <Router history={history}>
      <App />
    </Router>,
  )
  const user = userEvent.setup()
  // verify page content for expected route
  // often you'd use a data-testid or role query, but this is also possible
  expect(screen.getByText(/you are home/i)).toBeInTheDocument()

  await user.click(screen.getByText(/about/i))

  // check that the content changed to the new page
  expect(screen.getByText(/you are on the about page/i)).toBeInTheDocument()
})

test('landing on a bad page', () => {
  const history = createMemoryHistory()
  history.push('/some/bad/route')
  render(
    <Router history={history}>
      <App />
    </Router>,
  )

  expect(screen.getByText(/no match/i)).toBeInTheDocument()
})
```

## React Transition Group
<!-- Topics: test transitions, animation testing, React Transition Group -->

<!-- Source: example-react-transition-group.md -->


## Mock

```jsx

function Fade({children, ...props}) {
  return (
    <CSSTransition {...props} timeout={1000} classNames="fade">
      {children}
    </CSSTransition>
  )
}

function HiddenMessage({initialShow}) {
  const [show, setShow] = useState(initialShow || false)
  const toggle = () => setShow(prevState => !prevState)
  return (
    <div>
      <button onClick={toggle}>Toggle</button>
      <Fade in={show}>
        <div>Hello world</div>
      </Fade>
    </div>
  )
}

jest.mock('react-transition-group', () => {
  const FakeTransition = jest.fn(({children}) => children)
  const FakeCSSTransition = jest.fn(props =>
    props.in ? <FakeTransition>{props.children}</FakeTransition> : null,
  )
  return {CSSTransition: FakeCSSTransition, Transition: FakeTransition}
})

test('you can mock things with jest.mock', () => {
  const {getByText, queryByText} = render(<HiddenMessage initialShow={true} />)
  expect(getByText('Hello world')).toBeTruthy() // we just care it exists
  // hide the message
  fireEvent.click(getByText('Toggle'))
  // in the real world, the CSSTransition component would take some time
  // before finishing the animation which would actually hide the message.
  // So we've mocked it out for our tests to make it happen instantly
  expect(queryByText('Hello World')).toBeNull() // we just care it doesn't exist
})
```

## Shallow

```jsx

function Fade({children, ...props}) {
  return (
    <CSSTransition {...props} timeout={1000} classNames="fade">
      {children}
    </CSSTransition>
  )
}

function HiddenMessage({initialShow}) {
  const [show, setShow] = useState(initialShow || false)
  const toggle = () => setShow(prevState => !prevState)
  return (
    <div>
      <button onClick={toggle}>Toggle</button>
      <Fade in={show}>
        <div>Hello world</div>
      </Fade>
    </div>
  )
}

jest.mock('react-transition-group', () => {
  const FakeCSSTransition = jest.fn(() => null)
  return {CSSTransition: FakeCSSTransition}
})

test('you can mock things with jest.mock', () => {
  const {getByText} = render(<HiddenMessage initialShow={true} />)
  const context = expect.any(Object)
  const children = expect.any(Object)
  const defaultProps = {children, timeout: 1000, className: 'fade'}
  expect(CSSTransition).toHaveBeenCalledWith(
    {in: true, ...defaultProps},
    context,
  )
  fireEvent.click(getByText(/toggle/i))
  expect(CSSTransition).toHaveBeenCalledWith(
    {in: false, ...defaultProps},
    expect.any(Object),
  )
})
```

## Updating Props
<!-- Topics: update props in test, rerender with props, prop updates -->

<!-- Source: example-update-props.md -->

sidebar_label: Update Props

```jsx
// This is an example of how to update the props of a rendered component.
// the basic idea is to simply call `render` again and provide the same container
// that your first call created for you.


let idCounter = 1

const NumberDisplay = ({number}) => {
  const id = useRef(idCounter++) // to ensure we don't remount a different instance

  return (
    <div>
      <span data-testid="number-display">{number}</span>
      <span data-testid="instance-id">{id.current}</span>
    </div>
  )
}

test('calling render with the same component on the same container does not remount', () => {
  const {rerender} = render(<NumberDisplay number={1} />)
  expect(screen.getByTestId('number-display')).toHaveTextContent('1')

  // re-render the same component with different props
  rerender(<NumberDisplay number={2} />)
  expect(screen.getByTestId('number-display')).toHaveTextContent('2')

  expect(screen.getByTestId('instance-id')).toHaveTextContent('1')
})
```
