/* Home page for the application */

import '../index.css';
import React, {useEffect, useRef, useState} from 'react';
import ClustersMap from "../Map/ClustersMap";
import {Stage} from "@pixi/react";
import StickyBar from "../Navigation/StickyBar"
import NeighborsCarousel from "../Carousel/Carousel";
import ReactLoading from "react-loading";
import Typography from "@mui/material/Typography";
import {TfiAngleDown, TfiAngleUp} from "react-icons/tfi";
import {
    getButtonSize,
    getCarouselContainerMarginBottom,
    getCarouselContainerMarginTop,
    getResponsiveMargin,
} from "../utilities";
// import HamburgerMenu from "../Navigation/HamburgerMenu";


const MIN_HEIGHT = 900;
const ASPECT_RATIO = 16 / 9;
const STAGE_MAX_ASP_RATIO = 8 / 3;

function fetchAvailableDatasets(host) {
    let url = host + '/api/collection-names';

    return fetch(url, {
        method: 'GET'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Dataset names could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            // Fetch dataset info for each dataset
            let fetchPromises = data.collections.map(collection => {
                let url = host + '/api/collection-info?collection=' + collection["name"];
                return fetch(url, {
                    method: 'GET'
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Dataset info could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
                        }
                        return response.json();
                    })
                    .then(info => {
                        return {collection, zoom_levels: info.zoom_levels};
                    });
            });

            return Promise.all(fetchPromises)
                .then(results => {
                    let datasets_info = new Map();
                    results.forEach(result => {
                        datasets_info.set(result.collection, result.zoom_levels);
                    });
                    return {
                        collections: data.collections,
                        collections_info: datasets_info
                    };
                })
                .catch(error => {
                    // Handle any errors that occur during the fetch operation
                    console.error('Error:', error);
                });
        })
        .catch(error => {
            // Handle any errors that occur during the fetch operation
            console.error('Error:', error);
        });
}

const computeStageDimensions = () => {
    const height = window.innerHeight /*- getResponsiveHeight().replace('px', '')*/
        - getCarouselContainerMarginTop().replace('px', '') - getCarouselContainerMarginBottom().replace('px', '')
        - getButtonSize().replace('px', '');

    const width = Math.min(window.innerWidth - 2 * getResponsiveMargin().replace('px', ''), height * STAGE_MAX_ASP_RATIO);

    return {
        width: width,
        height: height
    };
}

const computeEmbeddingStateDimensions = () => {
    // First, get height, then adjust width based on aspect ratio
    const height = Math.max(window.innerHeight /*- getResponsiveHeight().replace('px', '')*/
        - getCarouselContainerMarginTop().replace('px', '') - getCarouselContainerMarginBottom().replace('px', '')
        - getButtonSize().replace('px', ''), MIN_HEIGHT);
    const width = Math.ceil(height * ASPECT_RATIO);

    return {
        width: width,
        height: height
    };
}

const Home = (props) => {
    // Define state for the dimensions of the stage
    const [dimensionsStage, setDimensionsStage] = useState(computeStageDimensions());
    // Define state for the dimensions of the embedding state
    const [dimensionsEmbeddingState, setDimensionsEmbeddingState] = useState(computeEmbeddingStateDimensions());
    // Define state for the overflow along the x-axis
    const [overflowX, setOverflowX] = useState(dimensionsEmbeddingState.width - dimensionsStage.width);
    const [overflowY, setOverflowY] = useState(dimensionsEmbeddingState.height - dimensionsStage.height);
    // Define host
    let host = useRef(props.host);
    // Define data from text search
    const [searchData, setSearchData] = useState({});
    // Define state for blocking search bar during loading or other operations
    const [searchBarIsBlocked, setSearchBarIsBlocked] = useState(false);
    // Define state for ongoing request of tile after text search or swipe up
    const [onGoingRequest, setOnGoingRequest] = useState(false);
    // Define boolean for showing the carousel with the nearest neighbors of a clicked image
    const [showCarousel, setShowCarousel] = useState(false);
    // Define variable for storing the index of the clicked image
    const [clickedImageIndex, setClickedImageIndex] = useState(-1);
    const prevClickedImageIndex = useRef(-1);
    // Define state for datasets
    const [datasets, setDatasets] = useState([]);
    // Define state for selected dataset
    const [selectedDataset, setSelectedDataset] = useState(null);
    // Define state for dataset info
    const [datasetInfo, setDatasetInfo] = useState(null);
    // Define state to know if initial loading is done
    const [initialLoadingDone, setInitialLoadingDone] = useState(false);
    // Define state for change of page
    const [pageHasChanged, setPageHasChanged] = useState(false);
    // Define ref for previous page
    const prevPage = useRef(props.page);
    // Define state for making the stage not interactive during a search
    const [stageIsInteractive, setStageIsInteractive] = useState(true);
    // Define state for upload div open
    const [uploadDivOpen, setUploadDivOpen] = useState(false);

    useEffect(() => {
        // Define function for updating the dimensions of the stage
        const updateDimensions = () => {
            const newDimensionsStage = computeStageDimensions();
            const newDimensionsEmbeddingState = computeEmbeddingStateDimensions();
            setDimensionsStage(newDimensionsStage);
            setDimensionsEmbeddingState(newDimensionsEmbeddingState);
            setOverflowX(newDimensionsEmbeddingState.width - newDimensionsStage.width);
            setOverflowY(newDimensionsEmbeddingState.height - newDimensionsStage.height);
        };
        // Add event listener
        window.addEventListener('resize', updateDimensions);

        // Fetch available datasets
        fetchAvailableDatasets(host.current)
            .then(data => {
                setDatasets(data.collections);
                setSelectedDataset(data.collections[0]);
                setDatasetInfo(data.collections_info);

            })
            .catch(error => {
                console.error('Error:', error);
            });

        // Return cleanup function for removing the event listener
        return () => {
            window.removeEventListener('resize', updateDimensions);
        };
    }, []);

    useEffect(() => {
        if (props.page === "about" && prevPage.current === "home") {
            setPageHasChanged(true);
            setShowCarousel(false);
            prevPage.current = "about";
        }
    }, [props.page]);

    useEffect(() => {
        setPageHasChanged(false);
        prevPage.current = "home";
        // Show carousel if the clicked image index is different from -1
        if (clickedImageIndex !== -1) {
            setShowCarousel(true);
            prevClickedImageIndex.current = clickedImageIndex;
        }
    }, [clickedImageIndex]);

    return (
        <>
            {(selectedDataset !== null && datasetInfo.get(selectedDataset) !== undefined) &&
                <div hidden={props.page !== "home" || !initialLoadingDone} id="home">
                    <StickyBar host={host.current}
                               hasSearchBar={true}
                               setSearchData={setSearchData}
                               setShowCarousel={setShowCarousel}
                               datasets={datasets}
                               selectedDataset={selectedDataset}
                               setSelectedDataset={setSelectedDataset}
                               page={props.page}
                               setPage={props.setPage}
                               searchBarIsClicked={props.searchBarIsClicked}
                               setSearchBarIsClicked={props.setSearchBarIsClicked}
                               searchBarIsBlocked={searchBarIsBlocked}
                               onGoingRequest={onGoingRequest}
                               setOnGoingRequest={setOnGoingRequest}
                               setStageIsInteractive={setStageIsInteractive}
                               setUploadDivOpen={setUploadDivOpen}
                               setClickedImageIndex={setClickedImageIndex}
                    />
                    {/*<HamburgerMenu*/}
                    {/*    menuOpen={menuOpen}*/}
                    {/*    setMenuOpen={setMenuOpen}*/}
                    {/*    datasets={datasets}*/}
                    {/*    setSelectedDataset={setSelectedDataset}*/}
                    {/*    setPage={props.setPage}*/}
                    {/*/>*/}
                    {/*<div className="bg-black flex flex-col items-center justify-center mt-sticky m-canvas-side mainContentOpacity">*/}
                    <div className="bg-black flex flex-col items-center justify-center m-canvas-top m-canvas-side">
                        <Stage width={dimensionsStage.width}
                               height={dimensionsStage.height}
                               raf={true}
                               renderOnComponentChange={false}
                               options={{backgroundColor: 0x000000, antialias: true}}>
                            <ClustersMap width={dimensionsEmbeddingState.width}
                                         height={dimensionsEmbeddingState.height}
                                         overflowX={overflowX}
                                         overflowY={overflowY}
                                         stageWidth={dimensionsStage.width}
                                         stageHeight={dimensionsStage.height}
                                         host={host.current}
                                         selectedDataset={selectedDataset}
                                         maxZoomLevel={datasetInfo.get(selectedDataset)}
                                         searchData={searchData}
                                         showCarousel={showCarousel}
                                         setShowCarousel={setShowCarousel}
                                         prevClickedImageIndex={prevClickedImageIndex}
                                         clickedImageIndex={clickedImageIndex}
                                         setClickedImageIndex={setClickedImageIndex}
                                         setInitialLoadingDone={setInitialLoadingDone}
                                         searchBarIsClicked={props.searchBarIsClicked}
                                         setSearchBarIsBlocked={setSearchBarIsBlocked}
                                         stageIsInteractive={stageIsInteractive}
                                         setStageIsInteractive={setStageIsInteractive}
                                         uploadDivOpen={uploadDivOpen}
                                         setUploadDivOpen={setUploadDivOpen}
                            />
                        </Stage>
                        <div
                            className="w-full bg-transparent carousel-container flex flex-col items-center justify-center z-50"
                            style={
                                {
                                    marginTop: {showCarousel} ? '0' : getCarouselContainerMarginTop(),
                                    position: 'absolute',
                                    bottom: {showCarousel} ? getCarouselContainerMarginBottom() : '-100%'
                                }
                            }>
                            {clickedImageIndex !== -1 && (
                                <button
                                    className="mb-1 flex flex-row items-center justify-center button pointer-events-auto"
                                    onPointerDown={() => {
                                        if (clickedImageIndex !== -1) {
                                            setShowCarousel(!showCarousel);
                                            prevClickedImageIndex.current = clickedImageIndex;
                                        }
                                        setPageHasChanged(false);
                                        prevPage.current = "home";
                                    }}>
                                    {showCarousel ?
                                        <TfiAngleDown style={{zIndex: 1000, fontWeight: 2000}}
                                                      className="text-white button"/> :
                                        <TfiAngleUp style={{zIndex: 1000}} className="text-white button"/>}
                                </button>
                            )}
                            <div id="carousel-id"
                                 className={`bg-transparent carousel-div max-h-carousel-plus-image flex flex-col items-center justify-center pointer-events-none
                                 ${!pageHasChanged ? (showCarousel && clickedImageIndex !== -1 ? 'height-transition open' : 'height-transition close') : ''}
                                 ${pageHasChanged ? 'max-height-transition-close' : ''}`} style={{zIndex: 40}}>
                                {clickedImageIndex !== -1 &&
                                    <NeighborsCarousel host={host.current} clickedImageIndex={clickedImageIndex}
                                                       setClickedImageIndex={setClickedImageIndex}
                                                       selectedDataset={selectedDataset}
                                                       setSearchData={setSearchData}
                                                       setShowCarousel={setShowCarousel}
                                                       onGoingRequest={onGoingRequest}
                                                       setOnGoingRequest={setOnGoingRequest}
                                                       setStageIsInteractive={setStageIsInteractive}/>}
                            </div>
                        </div>
                    </div>
                </div>}
            {(selectedDataset === null || datasetInfo.get(selectedDataset) === undefined || !initialLoadingDone) &&
                <div className="bg-black flex flex-col items-center justify-center w-screen h-screen">
                    <ReactLoading type="spinningBubbles" color="#ffffff" height={100} width={100}/>
                    <Typography variant="h1" sx={{
                        backgroundColor: 'black',
                        fontSize: 'calc(min(3vh, 3vw))',
                        fontStyle: 'italic',
                        fontWeight: 'bold',
                        fontFamily: 'Roboto Slab, serif',
                        textAlign: 'center',
                        color: 'white',
                        marginTop: '2%'
                    }}>
                        Painting...
                    </Typography>
                </div>}
        </>
    );
}


export default Home;
