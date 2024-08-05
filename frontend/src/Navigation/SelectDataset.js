import * as React from 'react';
import {useEffect} from 'react';
import {GoDatabase} from "react-icons/go";
import {iconStyle, itemsStyle} from "../styles";
import {Unstable_Popup as BasePopup} from '@mui/base/Unstable_Popup';


const SelectDataset = (props) => {
    const [dataset, setDataset] = React.useState(props.datasets !== undefined ? props.datasets[0] : undefined);
    const [anchor, setAnchor] = React.useState(null);
    const [open, setOpen] = React.useState(false);

    useEffect(() => {
        const closePopup = (event) => {
            if (!event.target.id.endsWith("dataset") || event.target.id === undefined) {
                setOpen(false);
            } else if (event.target.id === "icon-dataset") {
                setOpen(true);
                setAnchor(anchor ? null : event.target);
            }
        }
        window.addEventListener('click', closePopup);
        window.addEventListener('touchstart', closePopup);
        return () => {
            window.removeEventListener('click', closePopup);
            window.removeEventListener('touchstart', closePopup);
        }
    }, []);

    const handleChange = (dataset) => {
        props.removeUploadDiv();
        setDataset(dataset);
        props.setClickedImageIndex(-1);
        props.setShowCarousel(false);
        props.setSelectedDataset(dataset);
        setOpen(false);
    };

    return (
        <div style={{zIndex: 100, pointerEvents: "auto"}}>
            <div id="icon-dataset" className="pointer-events-auto">
                <GoDatabase style={iconStyle} className="pointer-events-none"/>
            </div>
            <BasePopup id="popup-dataset" open={open} anchor={anchor} placement={"bottom-start"} style={{
                backgroundColor: "rgb(39, 39, 42)",
                border: "2px solid #303030",
                borderRadius: "5px",
                padding: "6px",
                height: props.datasets !== undefined ? itemsStyle.height.replace("px", "") * props.datasets.length + "px" : "auto",
                width: itemsStyle.fontSize.replace("px", "") * 5.5 + "px",
                zIndex: 100
            }}>
                <div id="div-dataset" className="flex flex-col justify-start items-start w-full h-full">
                    {dataset && props.datasets.map((d, index) => {
                        return (
                            <button id={`button-${index}-dataset`} key={index} onTouchStart={() => handleChange(d)}
                                    onClick={() => handleChange(d)} style={
                                {
                                    height: itemsStyle.height.replace("px", "") + "px",
                                    fontSize: itemsStyle.fontSize.replace("px", "") * 0.6 + "px",
                                    fontWeight: itemsStyle.fontWeight,
                                    fontFamily: itemsStyle.fontFamily,
                                    marginLeft: itemsStyle.marginLeft,
                                    textAlign: itemsStyle.textAlign,
                                    lineHeight: 1,
                                    color: "white",
                                    textDecoration: d === dataset ? 'underline' : 'none'
                                }
                            }> {d["website_name"]}
                            </button>
                        );
                    })}
                </div>
            </BasePopup>
        </div>
    );
}

export default SelectDataset;

// import * as React from 'react';
// import {GoDatabase} from "react-icons/go";
// import {iconStyle, itemsStyle} from "../styles";
// import {TfiAngleDown, TfiAngleUp} from "react-icons/tfi";
// import {SlCheck} from "react-icons/sl";
//
//
// const angleStyle = {
//     zIndex: 100,
//     marginLeft: '15px'
// }
//
// const newIconStyle = {
//     width: iconStyle.width.replace("px", "") * 0.75 + "px",
//     height: iconStyle.height.replace("px", "") * 0.75 + "px",
// }
//
// const newItemStyle = {
//     height: itemsStyle.height.replace("px", "") * 0.75 + "px",
//     fontSize: itemsStyle.fontSize.replace("px", "") * 0.75 + "px",
//     fontWeight: itemsStyle.fontWeight,
//     fontFamily: itemsStyle.fontFamily,
//     marginLeft: itemsStyle.marginLeft,
//     textAlign: itemsStyle.textAlign,
//     lineHeight: 1
// }
//
// function cleanText(text) {
//     // Split text on underscore
//     let split_text = text.split('_');
//     // Create a new string with the first letter of each word capitalized
//     let cleaned_text = '';
//     for (let i = 0; i < split_text.length; i++) {
//         cleaned_text += split_text[i].charAt(0).toUpperCase() + split_text[i].slice(1) + ' ';
//     }
//     // Remove last space
//     cleaned_text = cleaned_text.slice(0, -1);
//     return cleaned_text;
// }
//
// export default function SelectDataset(props) {
//     const [dataset, setDataset] = React.useState(props.datasets !== undefined ? props.datasets[0] : undefined);
//     const [showDatasetList, setShowDatasetList] = React.useState(false);
//
//     const handleChange = (dataset) => {
//         console.log(dataset);
//         setDataset(dataset);
//         props.setSelectedDataset(dataset);
//     };
//
//     return (
//         <div className="flex flex-col items-start justify-items-start w-full">
//             {dataset !== undefined && (
//                 <div style={
//                     {
//                         marginBottom: "15px"
//                     }
//                 } className="flex flex-row items-center justify-items-start w-full">
//                     <GoDatabase style={iconStyle}/>
//                     <h1 style={itemsStyle}> Dataset </h1>
//                     <button onClick={() => setShowDatasetList(!showDatasetList)} style={
//                         {
//                             marginLeft: "auto"
//                         }
//                     }>
//                         {!showDatasetList ?
//                             <TfiAngleDown style={angleStyle} className="text-white"/>
//                             :
//                             <TfiAngleUp style={angleStyle} className="text-white"/>
//                         }
//                     </button>
//                 </div>
//             )}
//             {showDatasetList && dataset && props.datasets.map((d, index) => {
//                 return (
//                     <div style={
//                         {
//                             marginLeft: iconStyle.width.replace("px", "") * 1.6 + "px",
//                             marginBottom: "10px"
//                         }
//                     } className="flex flex-row items-center justify-items-start w-full" key={index}>
//                         <button onClick={() => handleChange(d)}>
//                             <SlCheck style={newIconStyle} color={
//                                 d === dataset ?
//                                     "green"
//                                     :
//                                     "white"
//                             }/>
//                         </button>
//                         <h1 style={newItemStyle}> {cleanText(d)} </h1>
//                     </div>
//                 );
//             })}
//         </div>
//     );
// }