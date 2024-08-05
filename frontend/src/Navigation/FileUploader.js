import React, {useEffect, useRef, useState} from 'react';
import {useDropzone} from 'react-dropzone';
import CheckOutlinedIcon from '@mui/icons-material/CheckOutlined';
import ClearOutlinedIcon from '@mui/icons-material/ClearOutlined';
import {IconButton} from "@mui/material";

const getSizeSection = () => {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return {width: 280, height: 220};
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return {width: 400, height: 320};
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return {width: 500, height: 350};
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return {width: 600, height: 420}
        case document.documentElement.clientWidth > 1200:
            return {width: 600, height: 420}
        default:
            return {width: 600, height: 420};
    }
}

const getSizeThumbsContainer = () => {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return {width: 210, height: 150};
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return {width: 300, height: 210};
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return {width: 375, height: 262};
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return {width: 450, height: 315};
        case document.documentElement.clientWidth > 1200:
            return {width: 450, height: 315};
        default:
            return {width: 450, height: 315};
    }
}

const getFontSize = () => {
    switch (true) {
        case document.documentElement.clientWidth >= 320 && document.documentElement.clientWidth <= 480:
            return 14;
        case document.documentElement.clientWidth > 480 && document.documentElement.clientWidth <= 768:
            return 14;
        case document.documentElement.clientWidth > 768 && document.documentElement.clientWidth <= 1024:
            return 16;
        case document.documentElement.clientWidth > 1024 && document.documentElement.clientWidth <= 1200:
            return 18;
        case document.documentElement.clientWidth > 1200:
            return 18;
        default:
            return 18;
    }

}


export default function Previews(props) {
    const [files, setFiles] = useState([]);
    const host = useRef(props.host);
    const {getRootProps, getInputProps} = useDropzone({
        accept: {
            'image/jpeg': [],
            'image/png': []
        },
        onDrop: acceptedFiles => {
            setFiles(acceptedFiles.map(file => Object.assign(file, {
                preview: URL.createObjectURL(file)
            })));
        }
    });
    const searchBarIsBlocked = useRef(props.searchBarIsBlocked);
    const onGoingRequest = useRef(props.onGoingRequest);
    const [sizeSection, setSizeSection] = useState(getSizeSection());
    const [sizeThumbsContainer, setSizeThumbsContainer] = useState(getSizeThumbsContainer());
    const [fontSize, setFontSize] = useState(getFontSize());

    useEffect(() => {
        searchBarIsBlocked.current = props.searchBarIsBlocked;
    }, [props.searchBarIsBlocked]);

    useEffect(() => {
        onGoingRequest.current = props.onGoingRequest;
    }, [props.onGoingRequest]);

    useEffect(() => {
        // Define function to call when the component is resized
        function handleResize() {
            setSizeSection(getSizeSection());
            setSizeThumbsContainer(getSizeThumbsContainer());
            setFontSize(getFontSize());
        }

        // Add event listener to window
        window.addEventListener('resize', handleResize);

        // Remove event listener when component is unmounted
        return () => {
            window.removeEventListener('resize', handleResize);
        }
    }, []);

    const sendImage = (file) => {
        // Alert file type
        try {
            if (!file) return;
            props.setOnGoingRequest(true);
            props.setStageIsInteractive(false);
            // Create a form data object for the payload of the POST request
            const formData = new FormData();
            formData.append('file', file);
            const url = host.current + '/api/image-image' + '?collection=' + props.selectedDataset["name"];
            fetch(url, {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok)
                        throw new Error('Data could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
                    return response.json();
                })
                .then(firstGet => {
                    const url = host.current + '/api/image-to-tile?index=' + firstGet.index + '&collection=' + props.selectedDataset["name"] + "_image_to_tile";
                    return fetch(url, {
                        method: 'GET'
                    })
                        .then(response => {
                            if (!response.ok)
                                throw new Error('Data could not be retrieved. Status: ' + response.status + ' ' + response.statusText);
                            return response.json();
                        })
                        .then(secondGet => {
                            return {
                                firstGet: firstGet,
                                secondGet: secondGet
                            };
                        });
                })
                .then(result => {
                    // Group result into object with fields tile and image. Tile is an array of three elements, while image contains
                    // the global position of the image, and its width and height.
                    let groupedResult = {};
                    // noinspection JSUnresolvedVariable
                    groupedResult.tile = result.secondGet.tile;
                    groupedResult.image = {};
                    // noinspection JSUnresolvedVariable
                    groupedResult.image.x = result.firstGet.x;
                    // noinspection JSUnresolvedVariable
                    groupedResult.image.y = result.firstGet.y;
                    groupedResult.image.width = result.firstGet.width;
                    groupedResult.image.height = result.firstGet.height;
                    groupedResult.image.index = result.firstGet.index;
                    // Set result in parent component
                    props.setShowCarousel(false);
                    props.setSearchData(groupedResult);
                    props.setOnGoingRequest(false);
                })
                .catch(error => {
                    // Handle any errors that occur during the fetch operation
                    alert('Error: ' + error.message)
                    props.setOnGoingRequest(false);
                    props.setStageIsInteractive(true);
                })
                .catch(error => {
                    alert('Error: ' + error.message)
                    props.setOnGoingRequest(false);
                    props.setStageIsInteractive(true);
                });
        } catch (error) {
            alert('Error: ' + error.message)
            props.setOnGoingRequest(false);
            props.setStageIsInteractive(true);
        }
    }

    const thumbs = files.map(file => (
        <div key={file.name}>
            <img
                src={file.preview}
                style={{
                    height: '100%',
                    width: "100%",
                    objectFit: 'cover',
                }}
                // Revoke data uri after image is loaded
                onLoad={() => {
                    URL.revokeObjectURL(file.preview)
                }}
                alt={"img"}/>
        </div>
    ));

    useEffect(() => {
        // Make sure to revoke the data uris to avoid memory leaks, will run on unmount
        return () => files.forEach(file => URL.revokeObjectURL(file.preview));
    }, []);

    return (
        <div {...getRootProps({className: 'container'})} style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: files.length === 0 ? 0.7 * sizeSection.width : sizeSection.width,
            height: files.length === 0 ? 0.3 * sizeSection.height : sizeSection.height,
            backgroundColor: "white",
            borderWidth: 2,
            borderColor: files.length === 0 ? "rgb(102, 102, 102)" : "green",
            borderStyle: 'dashed',
            borderRadius: 5,
            cursor: 'pointer',
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-evenly",
            alignItems: "center"
        }}>
            <input {...getInputProps()} />
            <div style={{
                fontSize: fontSize,
                height: (sizeSection.height - sizeThumbsContainer.height) / 2,
                display: "grid",
                placeItems: "center"
            }}>
                <p>Choose a file or drag it here.</p>
            </div>
            {files.length > 0 &&
                <>
                    <div style={{
                        width: sizeThumbsContainer.width,
                        height: sizeThumbsContainer.height,
                        overflow: 'hidden',
                        borderRadius: 8,
                    }}>
                        {thumbs}
                    </div>
                    <div style={{
                        display: "flex",
                        flexDirection: "row",
                        justifyContent: "space-evenly",
                        alignItems: "center",
                        width: sizeThumbsContainer.width,
                        height: (sizeSection.height - sizeThumbsContainer.height) / 2
                    }}>
                        <IconButton type="button" onClick={(event) => {
                            event.stopPropagation();
                            setFiles([]);
                        }} style={
                            {
                                height: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8,
                                width: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8
                            }
                        }>
                            <ClearOutlinedIcon style={
                                {
                                    color: "red",
                                    height: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8,
                                    width: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8
                                }
                            }/>
                        </IconButton>
                        <IconButton type="button" onClick={(event) => {
                            event.stopPropagation();
                            if (searchBarIsBlocked.current || onGoingRequest.current) return;
                            props.removeUploadDiv();
                            sendImage(files[0]);
                            setFiles([]);
                        }} style={
                            {
                                height: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8,
                                width: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8
                            }
                        }>
                            <CheckOutlinedIcon style={
                                {
                                    color: "green",
                                    height: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8,
                                    width: ((sizeSection.height - sizeThumbsContainer.height) / 2) * 0.8
                                }
                            }/>
                        </IconButton>
                    </div>
                </>
            }
        </div>
    );
}
