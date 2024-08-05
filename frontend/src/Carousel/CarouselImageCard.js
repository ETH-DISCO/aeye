import * as React from 'react';
import './carousel.css';


export default function CarouselImageCard({url, setClickedImageIndex, index}) {
    return (
        <div id={url} style={{
            display: 'flex',
            flexDirection: 'column',
            marginLeft: '3%',
            marginRight: '3%',
            borderRadius: '10px',
            backgroundColor: "rgb(49 49 52 / 1)"
        }} className="h-carousel pointer-events-auto"
             onClick={
                 (event) => {
                     if (index !== -1)
                         setClickedImageIndex(index);
                     event.stopPropagation();
                 }
             }>
            {
                index !== -1 &&
                <img className="object-cover overflow-hidden"
                     style={
                         {
                             height: '100%',
                             width: '100%',
                             cursor: "pointer",
                             borderRadius: '10px',
                             border: "2px solid",
                             borderColor: "rgb(255 255 255 / 1)"
                         }
                     } src={url} alt="img"/>
            }
        </div>
    );
}