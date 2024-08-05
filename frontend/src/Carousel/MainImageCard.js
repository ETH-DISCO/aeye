import * as React from 'react';
import {useEffect, useRef} from 'react';
import ProgressiveImage from './ProgressiveImage';
import './carousel.css';
import {getMaxHeightMainImage} from "../utilities";
import TextArea from "./TextArea";

const MARGIN = 10;
const LINE_HEIGHT = 1.3;

const getHeightAndWidthOfMainImage = (height, width, has_text, marginFactor) => {
    // Get aspect ratio of the image
    const aspectRatio = height / width;
    // Get multiplicative factor
    const factor = has_text ? 0.9 : 1;
    const num_of_margins = has_text ? 3 : 2;
    // Get the maximum height of the main image
    const maxHeight = getMaxHeightMainImage() * factor - MARGIN * num_of_margins * marginFactor;
    // Get the maximum width of the main image
    const maxWidth = document.getElementById("carousel-id").offsetWidth * 0.9 - MARGIN * 2 * marginFactor;

    // Get aspect ratio of maximum height and width
    const aspectRatioMax = maxHeight / maxWidth;
    let newHeight, newWidth;
    if (aspectRatio > aspectRatioMax) {
        newHeight = maxHeight;
        newWidth = newHeight / aspectRatio;
    } else {
        newWidth = maxWidth;
        newHeight = newWidth * aspectRatio;
    }
    return {height: newHeight, width: newWidth};
}

const generateText = (image) => {
    let text = "";
    if (image.author !== undefined) {
        const author = image.author.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        text += "Artist: " + author + ".\n";
    }
    if (image.title !== undefined) {
        // Capitalize first letter of each word
        const title = image.title.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
        text += "Title: " + title + ".\n";
    }
    if (image.genre !== undefined)
        text += "Genre: " + image.genre + ".\n";

    if (image.date !== undefined)
        if (image.date !== -1) {
            text += "Date: " + image.date + ".\n";
        }
    if (image.caption !== undefined)
        text += "AI Caption: " + image.caption;

    return text;
}

function getFontSize(height) {
    // Change behavior of font size depending on device width and height of the available space
    switch (true) {
        case document.documentElement.clientWidth <= 480:
            if (height < 14 * LINE_HEIGHT * 2)
                // Have one line of text
                return Math.min(14, (height - 3) / LINE_HEIGHT);
            else
                return 14;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            if (height < 15 * 2 * LINE_HEIGHT)
                // Have one line of text
                return Math.min(15, (height - 3) / LINE_HEIGHT);
            else
                return 15;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            if (height < 16 * 2 * LINE_HEIGHT)
                // Have one line of text
                return Math.min(16, (height - 3) / LINE_HEIGHT);
            else
                return 16;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            if (height < 17 * 2 * LINE_HEIGHT)
                // Have one line of text
                return Math.min(17, (height - 3) / LINE_HEIGHT);
            else
                return 17;
        case document.documentElement.clientWidth > 1200:
            if (height < 18 * 2 * LINE_HEIGHT)
                // Have one line of text
                return Math.min(18, (height - 3) / LINE_HEIGHT);
            else
                return 18;
    }
}

function getMinWidth(text) {
    // Change behavior of min width depending on device width
    if (text === "")
        return 0;
    switch (true) {
        case document.documentElement.clientWidth <= 480:
            return "70%";
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return "60%";
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return "45%";
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return "35%";
        case document.documentElement.clientWidth > 1200:
            return "30%";
    }
}

function getStyle(heightAndWidth, factor, marginFactor, hasText) {
    return {
        backgroundColor: "transparent",
        color: 'white',
        cursor: 'pointer',
        maxHeight: factor !== 1 ? (getMaxHeightMainImage() - heightAndWidth.height * factor - 3 * MARGIN * marginFactor) + 'px' : 0,
        marginBottom: hasText ? MARGIN * marginFactor + 'px' : 0,
    }
}


export default function MainImageCard({
                                          image,
                                          placeholderSrc,
                                          src,
                                          host,
                                          selectedDataset,
                                          setSearchData,
                                          setShowCarousel,
                                          onGoingRequest,
                                          setOnGoingRequest,
                                          setStageIsInteractive,
                                          noText = false,
                                          marginFactor = 1
                                      }) {
    const [heightAndWidth, setHeightAndWidth] = React.useState({height: 0, width: 0});
    const [height, setHeight] = React.useState(window.innerHeight);
    const noTextRef = useRef(noText);
    const marginFactorRef = useRef(marginFactor);
    const [text, setText] = React.useState("");
    const [factor, setFactor] = React.useState(1);

    useEffect(() => {
        noTextRef.current = noText;
    }, [noText]);

    useEffect(() => {
        marginFactorRef.current = marginFactor;
    }, [marginFactor]);

    useEffect(() => {
        // Generate text for the image
        let t = "";
        if (!noTextRef.current) {
            t = generateText(image);
        }
        setText(t);
        // Check if there is text
        const has_text = t !== "";
        // Get height and width of the main image
        const {
            height,
            width
        } = getHeightAndWidthOfMainImage(image.height, image.width, has_text, marginFactorRef.current);
        setHeightAndWidth({height: height, width: width});
        // Set factor to 1 if there is no text, otherwise set it to 0.9
        setFactor(has_text ? 0.9 : 1);
    }, [image]);

    useEffect(() => {
        function handleResize() {
            setHeight(window.innerHeight);
        }

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);


    return (
        <div style={
            {
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'start',
                alignItems: 'center',
                borderRadius: '10px',
                minHeight: (heightAndWidth.height * factor + 2 * MARGIN * marginFactorRef.current) + "px",
                maxHeight: factor === 1 ? (heightAndWidth.height + 2 * MARGIN * marginFactorRef.current) + "px" : getMaxHeightMainImage() + "px",
                overflowY: "auto",
                scrollbarWidth: "none",
                width: heightAndWidth.width,
                minWidth: getMinWidth(text),
                backgroundColor: "rgb(49 49 52 / 1)",
                zIndex: 100,
                pointerEvents: "auto",
            }
        } className={height >= 500 ? "margin-between-images-bottom" : ""}
             onPointerDown={
                 (event) => {
                     event.stopPropagation();
                 }
             }>
            {image && image.index !== -1 &&
                <>
                    <ProgressiveImage
                        placeholderSrc={placeholderSrc}
                        src={src}
                        width={(heightAndWidth.width - MARGIN * 2 * marginFactorRef.current) + 'px'}
                        height={(heightAndWidth.height * factor) + 'px'}
                        margin={MARGIN * marginFactorRef.current}
                        image={image}
                        host={host}
                        selectedDataset={selectedDataset}
                        setSearchData={setSearchData}
                        setShowCarousel={setShowCarousel}
                        onGoingRequest={onGoingRequest}
                        setOnGoingRequest={setOnGoingRequest}
                        setStageIsInteractive={setStageIsInteractive}
                    />
                    <div style={getStyle(heightAndWidth, factor, marginFactorRef.current, text !== "")}>
                        <TextArea
                            text={text}
                            margin={MARGIN * marginFactorRef.current}
                            height={factor !== 1 ? (getMaxHeightMainImage() - heightAndWidth.height * factor - 3 * MARGIN * marginFactorRef.current) : 0}
                            fontsize={getFontSize(factor !== 1 ? (getMaxHeightMainImage() - heightAndWidth.height * factor - MARGIN * marginFactorRef.current) : 0)}
                            line_height={LINE_HEIGHT}/>
                    </div>
                </>}
        </div>
    );
}
