import React, {useEffect, useState} from 'react';
import {TfiClose} from "react-icons/tfi";
import {iconStyle} from "../../styles";
import ScatterPlot from "./ScatterPlot";
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';


const newIconStyle = {
    height: iconStyle.height.replace("px", "") * 0.7 + "px",
    width: iconStyle.width.replace("px", "") * 0.7 + "px",
    color: "black",
    position: "fixed",
    top: "5px",
    right: "5px",
    backgroundColor: "transparent",
    zIndex: 100,
    cursor: "pointer"
}

const liStyle = {
    listStyle: "decimal",
    listStylePosition: "inside",
    display: "list-item",
    marginBottom: "1em",
    fontSize: "1em",
    textAlign: "justify",
    hyphens: "auto",
    hyphenateLimitChars: "2 1 1"
}

function fetchImage(host) {
    // Sample random number between 0 and 1
    const num = Math.random();
    const url = `${host}/api/random-image?num=${num}&collection=best_artworks`;
    return fetch(url,
        {
            method: 'GET',
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            return data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function computeWidth() {
    switch (true) {
        case window.innerWidth < 640:
            return window.innerWidth * 0.8;
        case window.innerWidth < 768:
            return window.innerWidth * 0.7;
        case window.innerWidth < 1024:
            return window.innerWidth * 0.6;
        default:
            return window.innerWidth * 0.5;
    }
}

function getPlotSize() {
    switch (true) {
        case window.innerWidth < 640:
            return window.innerWidth * 0.8;
        case window.innerWidth < 768:
            return window.innerWidth * 0.7;
        case window.innerWidth < 1024:
            return window.innerWidth * 0.5;
        default:
            return window.innerWidth * 0.4;
    }
}


function getTextStyle(width) {
    return {
        marginTop: "1em",
        textAlign: "justify",
        font: "Computer Modern",
        fontSize: "1.2em",
        width: width + "px",
        lineHeight: "1.6",
        hyphens: "auto",
        hyphenateLimitChars: "2 1 1"
    }
}

function getBibliographyStyle(width) {
    return {
        marginTop: "1em",
        textAlign: "justify",
        font: "Computer Modern",
        fontSize: "0.8em",
        width: width + "px",
        lineHeight: "1.6",
        hyphens: "auto",
        hyphenateLimitChars: "2 1 1"
    }
}

const About = (props) => {
    const [width, setWidth] = useState(computeWidth());
    const [widthPlot, setWidthPlot] = useState(getPlotSize());
    const [n_neighbors, setNNeighbors] = useState(100);
    const [min_dist, setMinDist] = useState(0.1);
    const neigh_values = [3, 5, 10, 15, 20, 50, 100, 200];
    const min_dist_values = [0.0, 0.1, 0.25, 0.5, 0.8, 0.99];
    const [image, setImage] = useState("");
    const [caption, setCaption] = useState("");

    useEffect(() => {
        setWidth(computeWidth());

        const handleResize = () => {
            setWidth(computeWidth());
            setWidthPlot(getPlotSize());
        }

        // Add event listener to window
        window.addEventListener("resize", handleResize);
        // Remove event listener on cleanup
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    useEffect(() => {
        if (props.page === "about")
            fetchImage(props.host)
                .then((data) => {
                    setImage(props.host + "/best_artworks/" + data["path"]);
                    setCaption(data["caption"]);
                });
    }, [props.page]);

    const handleClick = () => {
        fetchImage(props.host)
            .then((data) => {
                setImage(props.host + "/best_artworks/" + data["path"]);
                setCaption(data["caption"]);
            });
    }

    const handleNeighborsChange = (sliderValue) => {
        setNNeighbors(neigh_values[sliderValue]);
    }

    const handleMinDistChange = (sliderValue) => {
        setMinDist(min_dist_values[sliderValue]);
    }

    return (
        <div hidden={props.page !== "about"} style={{overflow: "hidden", width: "100vw"}}>
            <TfiClose onClick={() => props.setPage("home")} style={newIconStyle}/>
            <div id="about-page" style={
                {
                    position: "absolute",
                    top: -parseInt(newIconStyle.height.replace("px", "")) + "px",
                    backgroundColor: "#f5f5dc",
                    textDecorationColor: "black",
                    width: "100%",
                    display: "grid",
                    placeItems: "center"
                }
            }>
                <h1 style={{font: "Computer Modern", fontSize: "2em", fontWeight: "bold", marginTop: "2em", textAlign: "center", width: "80vw"}}>
                    AEye: A Visualization Tool for Image Datasets
                </h1>
                <p style={getTextStyle(width)}>
                    In the realm of AI systems, the analysis and manipulation of images have become increasingly
                    indispensable across various applications. However, visualizing the high-dimensional vector
                    representations commonly used in machine learning poses a significant challenge. To address this, we
                    present a web tool designed for the visualization of images based on their vector embeddings. Our
                    tool
                    projects images onto a two-dimensional plane, leveraging the embeddings to enable intuitive
                    exploration.
                    Users can navigate the plane, conduct text-image matching, and interactively visualize images.
                </p>
                <h1 style={{
                    font: "Computer Modern",
                    fontSize: "2em",
                    marginTop: "1em",
                    textAlign: "left",
                    width: width + "px"
                }}>1. Background</h1>
                <p style={getTextStyle(width)}>
                    Over the years, art datasets have been used for a variety of tasks, from style, genre, and artist
                    prediction <sup>[1]</sup> to text-guided artistic generation <sup>[2]</sup> and style transfer
                    <sup>[3]</sup>. Our work focuses on the visualization of datasets based on the projection of image
                    embeddings onto the two dimensional plane.
                </p>
                <h1 style={{
                    font: "Computer Modern",
                    fontSize: "1.5em",
                    marginTop: "1em",
                    textAlign: "left",
                    width: width + "px"
                }}>1.1. CLIP</h1>
                <p style={getTextStyle(width)}>
                    The image embeddings in our project are generated using the CLIP <sup>[4]</sup> vision encoder, a
                    state-of-the-art
                    multi-modal model renowned for its ability to generalize well to unseen data. CLIP achieves this
                    through its extensive training on a diverse corpus of text-image pairs, enabling it to capture rich
                    semantic representations. Notably, CLIP has demonstrated remarkable transfer capabilities across
                    various tasks, often competing with fully supervised models without requiring task-specific training.
                    We leverage CLIP to embed images into 512-dimensional vectors using its vision encoder,
                    and utilize the text encoder for zero-shot matching of text and images.
                </p>
                <h1 style={{
                    font: "Computer Modern",
                    fontSize: "1.5em",
                    marginTop: "1em",
                    textAlign: "left",
                    width: width + "px"
                }}>1.2. UMAP</h1>
                <p style={getTextStyle(width)}>
                    UMAP (Uniform Manifold Approximation and Projection) <sup>[5]</sup> is a dimensionality reduction
                    technique that has gained widespread use due to its high-quality visualizations, preservation of
                    global structure, and efficient runtime performance. While other common techniques such as PCA
                    (Principal Component Analysis) <sup>[6]</sup> and t-SNE (t-distributed Stochastic Neighbor
                    Embedding) <sup>[7]</sup> are also employed for dimensionality reduction, both t-SNE and UMAP have
                    been shown to produce superior visualization results compared to PCA. However, we opt for UMAP over
                    t-SNE due to its significantly faster computational speed. Although this speed difference may seem
                    negligible for small datasets, it becomes crucial for larger datasets.
                    The plot shows the projection of the "Best Artworks of All Time" dataset <sup>[8]</sup> onto the two
                    dimensional plane. You can change the parameters n_neighbors and min_dist to see how the UMAP
                    projection changes.
                </p>
                { props.page === "about" &&
                <div style={{width: widthPlot + "px", marginTop: "2em"}}>
                    <ScatterPlot host={props.host} n_neighbors={n_neighbors} min_dist={min_dist}
                                 height={widthPlot} width={widthPlot}/>
                    <div className="flex flex-row justify-left items-center" style={{marginTop: "1em"}}>
                        <h1 style={{width: widthPlot * 0.5 + "px"}}>Neighbors={n_neighbors}</h1>
                        <Slider
                            style={{width: widthPlot * 0.5 + "px"}}
                            min={0}
                            max={neigh_values.length - 1}
                            defaultValue={6}
                            onChange={handleNeighborsChange}
                            styles={{track: {backgroundColor: "#0096c7"}, handle: {borderColor: "#0096c7", backgroundColor: "#0096c7"}}}
                        />
                    </div>
                    <div className="flex flex-row justify-left items-center" style={{marginTop: "1em"}}>
                        <h1 style={{width: widthPlot * 0.5 + "px"}}>Distance={min_dist}</h1>
                        <Slider
                            style={{width: widthPlot * 0.5 + "px"}}
                            min={0}
                            max={min_dist_values.length - 1}
                            defaultValue={1}
                            onChange={handleMinDistChange}
                            styles={{track: {backgroundColor: "#0096c7"}, handle: {borderColor: "#0096c7", backgroundColor: "#0096c7"}}}
                        />
                    </div>
                </div> }
                <h1 style={{
                    font: "Computer Modern",
                    fontSize: "1.5em",
                    marginTop: "1em",
                    textAlign: "left",
                    width: width + "px"
                }}>1.3. K-Means Clustering</h1>
                <p style={getTextStyle(width)}>
                    The k-means clustering algorithm <sup>[9]</sup> is one of the most widely used clustering
                    algorithms, dating back to the 1950s. In our approach, we employ a modified version of the algorithm
                    that maintains cluster representatives from one level to the next.
                </p>
                <h1 style={{
                    font: "Computer Modern",
                    fontSize: "1.5em",
                    marginTop: "1em",
                    textAlign: "left",
                    width: width + "px"
                }}>1.4. LLAVA</h1>
                <p style={getTextStyle(width)}>
                    LLaVA (Large Language-and-Vision Assistant) <sup>[10,11]</sup> is a multi-modal model designed to bridge
                    vision and language comprehension, enabling it to accurately answer questions based on image content.
                    Leveraging this capability, we utilize the model to generate descriptive captions for images,
                    prompted by a simple query format: "USER: &lt;image&gt; Describe the image. ASSISTANT:". In our work,
                    we employ the model with 7 billion parameters. The following tool shows the results of the LLaVA model
                    on the "Best Artworks of All Time" dataset. You can click on the image to get a new image and caption.
                </p>
                {
                    image !== "" && caption !== "" && props.page === "about" &&
                    <div style={{width: widthPlot + "px", marginTop: "1em", display: "grid", placeItems: "center"}}>
                        <img src={image} alt="Random image"
                             style={{maxWidth: widthPlot + "px", maxHeight: widthPlot * 0.8 + "px", cursor: "pointer"}}
                             onClick={handleClick} onTouchStart={handleClick}/>
                        <p style={
                            {
                                font: "Computer Modern",
                                fontSize: "0.9em",
                                marginTop: "1em",
                                textAlign: "justify",
                                fontStyle: "italic",
                                hyphens: "auto",
                                hyphenateLimitChars: "2 1 1"
                            }
                        }>
                            {caption}
                        </p>
                    </div>
                }
                <h1 style={{
                    font: "Computer Modern",
                    fontSize: "1.5em",
                    marginTop: "1em",
                    textAlign: "left",
                    width: width + "px",
                    borderTop: "1px solid black"
                }}>References</h1>
                <ol style={getBibliographyStyle(width)}>
                    <li style={liStyle}>
                        B. Saleh, and A. Elgammal, "Large-scale Classification of Fine-Art Paintings: Learning
                        The Right Metric on The Right Feature", arXiv preprint arXiv:1505.00855, 2015.
                    </li>
                    <li style={liStyle}>
                        R. Rombach, A. Blattmann, and B. Ommer, Text-Guided Synthesis of Artistic Images
                        with Retrieval-Augmented Diffusion Models, arXiv preprint arXiv:1505.00855, 2022.
                    </li>
                    <li style={liStyle}>
                        Y. Deng, F. Tang, W. Dong, C. Ma, X. Pan, L. Wang, and C. Xu, StyTr2:
                        Image Style Transfer with Transformers, arXiv preprint arXiv:2105.14576, 2021.
                    </li>
                    <li style={liStyle}>
                        A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal,
                        G. Sastry, A. Askell, P. Mishkin, J. Clark, G. Krueger, and I. Sutskever, Learning
                        Transferable Visual Models From Natural Language Supervision, arXiv preprint
                        arXiv:2103.00020,
                        2021.
                    </li>
                    <li style={liStyle}>
                        Leland McInnes, John Healy, and James Melville, UMAP: Uniform Manifold Approximation and
                        Projection for Dimension Reduction, arXiv preprint arXiv:1802.03426, 2018.
                    </li>
                    <li style={liStyle}>
                        Svante Wold, Kim Esbensen, and Paul Geladi, Principal component analysis, Psychometrika,
                        Chemometrics and Intelligent Laboratory Systems, vol. 2, no. 1, pp. 37–52, 1987.
                    </li>
                    <li style={liStyle}>
                        L. van der Maaten, and G. Hinton, Visualizing Data using t-SNE, Journal of Machine Learning
                        Research, vol. 9, no. 86, pp. 2579–2605, 2008.
                    </li>
                    <li style={liStyle}>
                        “Best artworks of all time.” [Online]. Available on kaggle.com.
                    </li>
                    <li style={liStyle}>
                        J. MacQueen, Some methods for classification and analysis of multivariate observations,
                        Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability,
                        vol. 1, no. 14, pp. 281–297, 1967.
                    </li>
                    <li style={liStyle}>
                        H. Liu, C. Li, Q. Wu, and Y. J. Lee, LLaVA: Visual instruction tuning, in NeurIPS, 2023.
                    </li>
                    <li style={liStyle}>
                        H. Liu, C. Li, Y. Li, and Y. J. Lee, Improved baselines with visual instruction tuning, 2023.
                    </li>
                </ol>
            </div>
        </div>
    );
}


export default About;