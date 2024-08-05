import {useEffect, useRef, useState} from "react";
import Hammer from "hammerjs";


const ProgressiveImg = ({placeholderSrc, src, width, height, margin, image, host, selectedDataset,
                            setSearchData, setShowCarousel, onGoingRequest, setOnGoingRequest,
                            setStageIsInteractive}) => {
    const [imgSrc, setImgSrc] = useState(placeholderSrc);
    const hammer = useRef(null);

    const getTileFromIndex = () => {
        setOnGoingRequest(true);
        setStageIsInteractive(false);
        let url = host + '/api/image-to-tile?index=' + image.index + '&collection=' + selectedDataset + "_image_to_tile";
        const options = {
            method: 'GET',
        };
        return fetch(url, options)
            .then(response => {
                if (!response.ok)
                    throw new Error('Data could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
                return response.json();
            })
            .then(data => {
                // Group result into object with fields tile and image. Tile is an array of three elements, while image contains
                // the global position of the image, and its width and height.
                let result = {};
                // noinspection JSUnresolvedVariable
                result.tile = data.tile;
                result.image = {};
                // noinspection JSUnresolvedVariable
                result.image.x = image.x;
                // noinspection JSUnresolvedVariable
                result.image.y = image.y;
                result.image.width = image.width;
                result.image.height = image.height;
                result.image.index = image.index;
                // Set result in parent component
                setShowCarousel(false);
                setSearchData(result);
                setOnGoingRequest(false);
            })
            .catch(error => {
                // Handle any errors that occur during the fetch operation
                console.error('Error:', error);
                setOnGoingRequest(false);
            });
    };

    useEffect(() => {
        hammer.current = new Hammer(document.getElementById("main-image"));
        hammer.current.get('swipe').set({direction: Hammer.DIRECTION_ALL});
        hammer.current.on('swipeup', () => {
            // Send index of main image to the server
            if (!onGoingRequest)
                // noinspection JSIgnoredPromiseFromCall
                getTileFromIndex();
        });
        hammer.current.on('tap', () => {
            window.open(src, '_blank');
        });
        return () => {
            if (hammer.current) {
                hammer.current.destroy();
            }
        };
    }, []);

    useEffect(() => {
        // Set the imgSrc to placeholderSrc initially
        setImgSrc(placeholderSrc);
        // Create a new image object
        const img = new Image();
        // Set the src of the image object to the src of the main image
        img.src = src;
        // When the main image finishes loading, set the imgSrc to the src of the main image
        img.onload = () => {
            setImgSrc(src);
        };
    }, [placeholderSrc, src]);

    return (
        <div id="main-image" style={{
            marginTop: margin,
            marginBottom: margin,
            width: width,
            height: height,
            cursor: imgSrc === src ? "pointer" : "auto",
        }}>
            <img
                {...{src: imgSrc}}
                alt={"Main image"}
                style={{
                    width: "100%",
                    height: "100%",
                    objectFit: "fill",
                    borderRadius: "5px"
                }}
                draggable={false}
            />
        </div>
    );
};
export default ProgressiveImg;