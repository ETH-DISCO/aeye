// Component for showing the nearest neighbors of an image on click or on search.

import React, {useEffect, useRef, useState} from 'react';
import Carousel from 'react-multi-carousel';
import CarouselImageCard from "./CarouselImageCard";
import 'react-multi-carousel/lib/styles.css';
import {getUrlForImage} from "../utilities";
import './carousel.css';
import MainImageCard from "./MainImageCard";


const NUM_OF_NEIGHBORS = 10;
const TEMP_ARRAY = Array(NUM_OF_NEIGHBORS).fill({
    path: "",
    index: -1,
    author: "",
    width: 1000,
    height: 1000,
    genre: "",
    title: "",
    date: -1
});

const responsive = {
    d1: {
        breakpoint: {
            max: 20000,
            min: 1201
        },
        items: 4
    },
    d2: {
        breakpoint: {
            max: 1200,
            min: 1025
        },
        items: 3
    },
    d3: {
        breakpoint: {
            max: 1024,
            min: 769
        },
        items: 3
    },
    d4: {
        breakpoint: {
            max: 768,
            min: 481
        },
        items: 3

    },
    d5: {
        breakpoint: {
            max: 480,
            min: 0
        },
        items: 2
    }
};

function fetchNeighbors(index, k, host, dataset) {
    // The function takes in an index of an image, and fetches the nearest neighbors of the image from the server.
    // Then it populates the state images with the fetched images.
    const url = `${host}/api/neighbors?index=${index}&k=${k}&collection=${dataset}`;
    return fetch(url,
        {
            method: 'GET',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Neighbors could not be retrieved from the server.' +
                    ' Please try again later. Status: ' + response.status + ' ' + response.statusText);
            }
            return response.json();
        })
        .catch(error => {
            // Handle any errors that occur during the fetch operation
            console.error('Error:', error);
        });
}


const NeighborsCarousel = (props) => {
    // Define state for images to show. The state consists of pairs (path, text), where path is the path to the image
    // and text is the text associated to the image.
    const [images, setImages] = useState(TEMP_ARRAY);
    const [image, setImage] = useState(TEMP_ARRAY[0]);
    const [height, setHeight] = useState(window.innerHeight);
    const selectedDataset = useRef(props.selectedDataset["name"]);

    useEffect(() => {
        const handleResize = () => {
            setHeight(window.innerHeight);
        }
        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        }
    }, []);

    useEffect(() => {
        // Empty the state images
        setImages(TEMP_ARRAY);
        setImage({
            path: "",
            index: -1,
            author: "",
            width: image.width,
            height: image.height,
            genre: "",
            title: "",
            date: -1
        });

        // Fetch neighbors from server
        fetchNeighbors(props.clickedImageIndex, NUM_OF_NEIGHBORS, props.host, selectedDataset.current)
            .then(data => {
                // Populate state images with the fetched images
                let images = [];
                let first = true;
                for (const image of data) {
                    // noinspection JSUnresolvedVariable
                    const new_image = {
                        path: image.path,
                        index: image.index,
                        author: image.author,
                        width: image.width,
                        height: image.height,
                        x: image.x,
                        y: image.y
                    }
                    // noinspection JSUnresolvedVariable
                    if (image.genre !== undefined)
                        // noinspection JSUnresolvedVariable
                        new_image.genre = image.genre;
                    // noinspection JSUnresolvedVariable
                    if (image.title !== undefined)
                        // noinspection JSUnresolvedVariable
                        new_image.title = image.title;
                    // noinspection JSUnresolvedVariable
                    if (image.date !== undefined)
                        // noinspection JSUnresolvedVariable
                        new_image.date = image.date;
                    // noinspection JSUnresolvedVariable
                    if (image.caption !== undefined)
                        // noinspection JSUnresolvedVariable
                        new_image.caption = image.caption;
                    // noinspection JSUnresolvedVariable
                    if (!first)
                        images.push(new_image);
                    else {
                        // noinspection JSUnresolvedVariable
                        setImage(new_image);
                        first = false;
                    }
                }
                setImages(images);
                return images
            })
    }, [props.clickedImageIndex]);

    useEffect(() => {
        selectedDataset.current = props.selectedDataset["name"];
        setImage(TEMP_ARRAY[0]);
        setImages(TEMP_ARRAY);
    }, [props.selectedDataset]);


    return (
        <>
            {/* Place space for the main image of the carousel */}
            {height > 500 && image &&
                <MainImageCard image={image}
                               placeholderSrc={getUrlForImage(image.path, selectedDataset.current, props.host)}
                               src={`${props.host}/${selectedDataset.current}/${image.path}`}
                               host={props.host}
                               selectedDataset={selectedDataset.current}
                               setSearchData={props.setSearchData}
                               setShowCarousel={props.setShowCarousel}
                               onGoingRequest={props.onGoingRequest}
                               setOnGoingRequest={props.setOnGoingRequest}
                               setStageIsInteractive={props.setStageIsInteractive}
                />
            }
            {height > 500 &&
                <div className="w-full h-carousel flex flex-row justify-center items-center pointer-events-none">
                    <Carousel
                        key={props.clickedImageIndex}
                        additionalTransfrom={0}
                        arrows
                        autoPlaySpeed={3000}
                        centerMode={false}
                        className="carousel"
                        containerClass="container"
                        dotListClass=""
                        draggable={false}
                        focusOnSelect={false}
                        infinite={false}
                        itemClass=""
                        keyBoardControl
                        minimumTouchDrag={10}
                        transitionDuration={300}
                        pauseOnHover
                        renderArrowsWhenDisabled={false}
                        renderButtonGroupOutside={false}
                        renderDotsOutside={false}
                        responsive={responsive}
                        rewind={false}
                        rewindWithAnimation={false}
                        rtl={false}
                        shouldResetAutoplay
                        showDots={false}
                        sliderClass=""
                        slidesToSlide={1}
                    >
                        {images.map((image, index) => {
                            return <CarouselImageCard
                                key={index}
                                url={getUrlForImage(image.path, selectedDataset.current, props.host)}
                                setClickedImageIndex={props.setClickedImageIndex}
                                index={image.index}/>
                        })}
                    </Carousel>
                </div>
            }
            {height <= 500 &&
                <div className="w-full pointer-events-none">
                    <Carousel
                        key={props.clickedImageIndex}
                        additionalTransfrom={0}
                        arrows
                        autoPlaySpeed={3000}
                        centerMode={false}
                        className="carousel"
                        containerClass="container"
                        dotListClass=""
                        draggable={false}
                        focusOnSelect={false}
                        infinite={false}
                        itemClass=""
                        keyBoardControl
                        minimumTouchDrag={10}
                        transitionDuration={300}
                        pauseOnHover
                        renderArrowsWhenDisabled={false}
                        renderButtonGroupOutside={false}
                        renderDotsOutside={false}
                        responsive={
                            {
                                d_all: {
                                    breakpoint: {
                                        max: 20000,
                                        min: 0
                                    },
                                    items: 1
                                }
                            }
                        }
                        rewind={false}
                        rewindWithAnimation={false}
                        rtl={false}
                        shouldResetAutoplay
                        showDots={false}
                        sliderClass=""
                        slidesToSlide={1}
                    >
                        {images.map((image, index) => {
                            return <div className="w-full h-full flex flex-row justify-center items-center"
                                        key={index} onClick={() => {}} onTouchStart={() => {}}>
                                <MainImageCard image={image}
                                               placeholderSrc={getUrlForImage(image.path, selectedDataset.current, props.host)}
                                               src={`${props.host}/${selectedDataset.current}/${image.path}`}
                                               host={props.host}
                                               selectedDataset={selectedDataset.current}
                                               setSearchData={props.setSearchData}
                                               setShowCarousel={props.setShowCarousel}
                                               onGoingRequest={props.onGoingRequest}
                                               setOnGoingRequest={props.setOnGoingRequest}
                                               setStageIsInteractive={props.setStageIsInteractive}
                                               noText={true}
                                               marginFactor={0.5}
                                />
                            </div>
                        })}
                    </Carousel>
                </div>
            }
        </>

    );
}

export default NeighborsCarousel;
