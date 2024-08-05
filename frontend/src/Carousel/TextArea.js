import * as React from 'react';


export default function TextArea({text, margin, height, fontsize, line_height}) {
    const textRef = React.useRef(null);

    return (
        <div style={
            {
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                borderRadius: '10px',
                maxHeight: height + 'px',
                width: "100%",
                paddingLeft: margin + 'px',
                paddingRight: margin + 'px',
                pointerEvents: "auto",
                backgroundColor: "rgb(49 49 52 / 1)"
            }
        }>
            <div ref={textRef} style=
                {
                    {
                        pointerEvents: "auto",
                        backgroundColor: "transparent",
                        fontFamily: 'Roboto Slab, serif',
                        fontSize: fontsize,
                        lineHeight: line_height,
                        hyphens: "auto",
                        textAlign: "justify",
                        hyphenateLimitChars: "2 1 1",
                        whiteSpace: "pre-wrap",
                        overflowX: "hidden",
                        overflowY: "auto",
                        height: 'auto',
                        scrollbarWidth: "none"
                    }
                }>
                {text}
            </div>
        </div>
    );
}