import './index.css';
import React, {useEffect, useRef, useState} from 'react';
import Home from "./Pages/Home";
import About from "./Pages/About/About";

function extractHost() {
    // Get host
    let in_host = window.location.href;
    // Remove trailing slash if present
    if (in_host.endsWith('/')) {
        in_host = in_host.substring(0, in_host.length - 1);
    }
    // Remove port from host. Keep http:// or https:// and the domain name, e.g. http://localhost
    // Get index of second colon
    let colon_count = 0;
    let i = 0;
    while (colon_count < 2 && i < in_host.length) {
        if (in_host[i] === ':') {
            colon_count++;
        }
        i++;
    }
    // If the last character is not a colon, add it to the host
    if (i === in_host.length) {
        in_host += ':';
        i++;
    }
    return in_host.substring(0, i) + '443';
}

function App() {
    // Define state for which page to show
    const [page, setPage] = useState("home");
    // Define state for search bar click. When the user clicks anywhere on the page, the search bar should move to its
    // position and the app should become usable.
    const [searchBarIsClicked, setSearchBarIsClicked] = useState(false);
    let host = useRef(extractHost());

    useEffect(() => {
        // Define event listener to handle click on the page. The event handler will be removed after the first click.
        const handleClick = (event) => {
            if ((event.target.id === "search-bar-id" || event.target.id === "search-button"
                    || event.target.id === "search-button-icon") && event.type !== "wheel")
                return;
            if (!searchBarIsClicked)
                setSearchBarIsClicked(true);
            window.removeEventListener('click', handleClick);
            window.removeEventListener('wheel', handleClick);
            window.removeEventListener('touchstart', handleClick);
        }

        // Add event listener to handle click or touch on the page or mouse wheel.
        window.addEventListener('click', handleClick);
        window.addEventListener('wheel', handleClick);
        window.addEventListener('touchstart', handleClick);
    }, []);

    return (
        <>
          <Home host={host.current} page={page} setPage={setPage} searchBarIsClicked={searchBarIsClicked} setSearchBarIsClicked={setSearchBarIsClicked}/>
          <About host={host.current} page={page} setPage={setPage}/>
        </>
    );
}


export default App;
