import React, { useState, useEffect, useRef, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader } from 'components/ui/Card';
import Button from '../ui/Button';

interface EquityCurveChartProps {
  equityCurve: { timestamp: string; equity: number }[];
  priceCurve?: { timestamp: string; price: number }[];
}

const EquityCurveChart: React.FC<EquityCurveChartProps> = ({ equityCurve, priceCurve }) => {
  const [chartType, setChartType] = useState<'equity' | 'price'>('equity');

  const processedData = useMemo(() => {
    const equityPoints = equityCurve.map(p => ({ timestamp: new Date(p.timestamp).getTime(), equity: p.equity }));
    const pricePoints = priceCurve ? priceCurve.map(p => ({ timestamp: new Date(p.timestamp).getTime(), price: p.price })) : [];

    const allTimestamps = [...new Set([...equityPoints.map(p => p.timestamp), ...pricePoints.map(p => p.timestamp)])].sort((a, b) => a - b);

    const dataMap = new Map<number, { equity?: number; price?: number }>();
    equityPoints.forEach(p => dataMap.set(p.timestamp, { ...dataMap.get(p.timestamp), equity: p.equity }));
    pricePoints.forEach(p => dataMap.set(p.timestamp, { ...dataMap.get(p.timestamp), price: p.price }));

    return allTimestamps.map(ts => ({
      timestamp: ts,
      equity: dataMap.get(ts)?.equity,
      price: dataMap.get(ts)?.price,
    }));
  }, [equityCurve, priceCurve]);

  const [left, setLeft] = useState<number | string>('dataMin');
  const [right, setRight] = useState<number | string>('dataMax');
  const [top, setTop] = useState<number | string>('dataMax');
  const [bottom, setBottom] = useState<number | string>('dataMin');
  
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number, left: number, right: number } | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);
  const [isHovering, setIsHovering] = useState(false);

  useEffect(() => {
    const chartElement = chartRef.current;
    if (!chartElement) return;

    const preventScroll = (e: WheelEvent) => {
      e.preventDefault();
    };

    if (isHovering) {
      chartElement.addEventListener('wheel', preventScroll, { passive: false });
    }

    return () => {
      chartElement.removeEventListener('wheel', preventScroll);
    };
  }, [isHovering]);

  const getDomain = () => {
    const dataMin = processedData.length > 0 ? processedData[0].timestamp : 0;
    const dataMax = processedData.length > 0 ? processedData[processedData.length - 1].timestamp : 0;
    const currentLeft = left === 'dataMin' ? dataMin : (left as number);
    const currentRight = right === 'dataMax' ? dataMax : (right as number);
    return { currentLeft, currentRight, dataMin, dataMax };
  };

  const updateYAxisDomain = (currentLeft: number, currentRight: number) => {
    const filteredData = processedData.filter(d => d.timestamp >= currentLeft && d.timestamp <= currentRight);
    if (filteredData.length > 0) {
      const values = filteredData.map(d => chartType === 'equity' ? d.equity : d.price).filter(v => v != null) as number[];
      if (values.length > 0) {
        const newBottom = Math.min(...values);
        const newTop = Math.max(...values);
        const padding = (newTop - newBottom) * 0.1 || 10;
        setBottom(newBottom - padding);
        setTop(newTop + padding);
      } else {
        setBottom('dataMin');
        setTop('dataMax');
      }
    } else {
      setBottom('dataMin');
      setTop('dataMax');
    }
  };

  const resetZoom = () => {
    setLeft('dataMin');
    setRight('dataMax');
    const { dataMin, dataMax } = getDomain();
    updateYAxisDomain(dataMin, dataMax);
  };

  useEffect(() => {
    resetZoom();
  }, [processedData, chartType]);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    
    const chartRect = chartRef.current?.getBoundingClientRect();
    if (!chartRect) return;
    const chartX = e.clientX - chartRect.left;

    if (chartX < 0 || chartX > chartRect.width) return;

    const { currentLeft, currentRight, dataMin, dataMax } = getDomain();
    const chartWidth = chartRect.width;
    const cursorTimestamp = currentLeft + (chartX / chartWidth) * (currentRight - currentLeft);

    const zoomFactor = 1.2;
    let newLeft, newRight;

    if (e.deltaY < 0) { // Zoom in
      newLeft = cursorTimestamp - (cursorTimestamp - currentLeft) / zoomFactor;
      newRight = cursorTimestamp + (currentRight - cursorTimestamp) / zoomFactor;
    } else { // Zoom out
      newLeft = cursorTimestamp - (cursorTimestamp - currentLeft) * zoomFactor;
      newRight = cursorTimestamp + (currentRight - cursorTimestamp) * zoomFactor;
    }

    if (newLeft < dataMin) newLeft = dataMin;
    if (newRight > dataMax) newRight = dataMax;
    if (newRight - newLeft < 1000 * 60 * 60 || newLeft >= newRight) return;

    setLeft(newLeft);
    setRight(newRight);
    updateYAxisDomain(newLeft, newRight);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    const { currentLeft, currentRight } = getDomain();
    setPanStart({ x: e.clientX, left: currentLeft, right: currentRight });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning || !panStart) return;
    const chartWidth = chartRef.current?.getBoundingClientRect().width || 1;
    const dx = e.clientX - panStart.x;
    const { dataMin, dataMax } = getDomain();
    const timeDelta = (dx / chartWidth) * (panStart.right - panStart.left);

    let newLeft = panStart.left - timeDelta;
    let newRight = panStart.right - timeDelta;

    if (newLeft < dataMin) {
      newLeft = dataMin;
      newRight = newLeft + (panStart.right - panStart.left);
    }
    if (newRight > dataMax) {
      newRight = dataMax;
      newLeft = newRight - (panStart.right - panStart.left);
    }

    setLeft(newLeft);
    setRight(newRight);
    updateYAxisDomain(newLeft, newRight);
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setPanStart(null);
  };

  const handleMouseLeave = () => {
    setIsPanning(false);
    setPanStart(null);
    setIsHovering(false);
  };

  const formatXAxis = (tickItem: number) => new Date(tickItem).toLocaleDateString();
  const formatYAxis = (tickItem: number) => tickItem.toLocaleString(undefined, { style: 'currency', currency: 'USD' });

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-semibold">{chartType === 'equity' ? 'Equity Curve' : 'Price Chart'}</h2>
            <p className="text-sm text-gray-500">Scroll to zoom, drag to pan, double-click to reset.</p>
          </div>
          {priceCurve && priceCurve.length > 0 && (
            <div className="flex space-x-2">
                <Button onClick={() => setChartType('equity')} variant={chartType === 'equity' ? 'primary' : 'secondary'} size="sm">Equity</Button>
                <Button onClick={() => setChartType('price')} variant={chartType === 'price' ? 'primary' : 'secondary'} size="sm">Price</Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div 
          ref={chartRef}
          onWheel={handleWheel} 
          onDoubleClick={resetZoom} 
          onMouseDown={handleMouseDown}
          onMouseMove={isPanning ? handleMouseMove : undefined}
          onMouseUp={handleMouseUp}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={handleMouseLeave}
          style={{ cursor: isPanning ? 'grabbing' : 'grab' }}
        >
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                allowDataOverflow 
                dataKey="timestamp" 
                domain={[left, right]} 
                type="number" 
                tickFormatter={formatXAxis} 
                scale="time"
              />
              <YAxis 
                allowDataOverflow 
                domain={[bottom, top]} 
                type="number" 
                tickFormatter={formatYAxis}
                width={80}
              />
              <Tooltip
                labelFormatter={formatXAxis}
                formatter={(value: number, name: string) => [formatYAxis(value), name.charAt(0).toUpperCase() + name.slice(1)]}
                position={isPanning ? { x: -1000, y: -1000 } : undefined}
              />
              <Legend />
              <Line type="monotone" dataKey={chartType} stroke="#8884d8" dot={false} animationDuration={0} name={chartType.charAt(0).toUpperCase() + chartType.slice(1)} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default EquityCurveChart;
