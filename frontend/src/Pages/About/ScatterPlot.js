import React, {useEffect, useRef, useState} from 'react';
import * as d3 from 'd3';
import {LRUCache} from "lru-cache";

function getCircleRadius() {
    switch (true) {
        case window.innerWidth < 640:
            return 0.5;
        case window.innerWidth < 768:
            return 0.7;
        case window.innerWidth < 1024:
            return 1;
        default:
            return 1.3;
    }
}

function getScatterPlotData(url, cache) {
    if (cache.has(url)) {
        return Promise.resolve(cache.get(url));
    }
    else {
        return fetch(url,
            {
                method: 'GET',
            })
            .then(response => {
                return response.json();
            })
            .then(data => {
                // Get x and y coordinates from the data
                const x = data["x"];
                const y = data["y"];
                let scatterPlotData = [];
                for (let i = 0; i < x.length; i++)
                    scatterPlotData.push({x: x[i], y: y[i]});
                // Add data to cache
                cache.set(url, scatterPlotData);
                return scatterPlotData;
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }
}

const ScatterPlot = ({host, n_neighbors, min_dist, height, width}) => {
    const ref = useRef();
    const [prevScales, setPrevScales] = useState({xScale: null, yScale: null});
    const [radius, setRadius] = useState(getCircleRadius());
    // Create LRU cache for scatter plot data
    const scatterPlotData = useRef(new LRUCache({
        max: 5,
        updateAgeOnHas: true,
        updateAgeOnGet: true
    }));

    useEffect(() => {
        const handleResize = () => {
            setRadius(getCircleRadius());
        };
        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    useEffect(() => {
        const url = `${host}/api/umap?n_neighbors=${n_neighbors}&min_dist=${min_dist}`;
        getScatterPlotData(url, scatterPlotData.current)
            .then((data) => {
                // noinspection JSUnresolvedFunction
                const xMax = d3.max(data, d => d.x);
                // noinspection JSUnresolvedFunction
                const xMin = d3.min(data, d => d.x);
                // noinspection JSUnresolvedFunction
                const yMax = d3.max(data, d => d.y);
                // noinspection JSUnresolvedFunction
                const yMin = d3.min(data, d => d.y);
                // noinspection JSUnresolvedFunction
                const xScale = d3.scaleLinear().domain([xMin - 1, xMax + 1]).range([0, width]);
                // noinspection JSUnresolvedFunction
                const yScale = d3.scaleLinear().domain([yMin - 1, yMax + 1]).range([0, height]);
                // noinspection JSUnresolvedFunction
                d3.select(ref.current)
                    .selectAll('circle')
                    .data(data)
                    .join(
                        enter => enter.append('circle')
                            .style('fill', '#0096c7')
                            .attr('cx', d => prevScales.xScale ? prevScales.xScale(d.x) : xScale(d.x))
                            .attr('cy', d => prevScales.yScale ? prevScales.yScale(d.y) : yScale(d.y))
                            .attr('r', radius),
                        update => update,
                        exit => exit.remove()
                    )
                    .transition()
                    .duration(300)
                    .attr('cx', d => xScale(d.x))
                    .attr('cy', d => yScale(d.y));

                setPrevScales({xScale, yScale});
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }, [n_neighbors, min_dist, height, width, radius]);

    return <svg ref={ref} height={height} width={width}></svg>
}

export default ScatterPlot;