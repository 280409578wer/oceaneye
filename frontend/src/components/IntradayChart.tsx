import * as echarts from "echarts";
import { useEffect, useMemo, useRef } from "react";
import type { MetricKey, TimePoint } from "../types";

const META: Record<MetricKey, { label: string; color: string; unit: string }> = {
  cost: { label: "消耗", color: "#58a6ff", unit: "¥" },
  clicks: { label: "点击", color: "#8b7cff", unit: "" },
  impressions: { label: "展示", color: "#5fb7b2", unit: "" },
  ctr: { label: "CTR", color: "#42c68a", unit: "%" },
  conversions: { label: "转化", color: "#42c68a", unit: "" },
  cpa: { label: "CPA", color: "#f0a65a", unit: "¥" },
  cvr: { label: "CVR", color: "#c68cff", unit: "%" },
};

interface IntradayChartProps {
  data: TimePoint[];
  metric: MetricKey;
}

export function IntradayChart({ data, metric }: IntradayChartProps) {
  const elementRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<echarts.ECharts | null>(null);
  const meta = META[metric];
  const points = useMemo(
    () => data.map((point) => [new Date(point.timestamp).getTime(), point[metric] ?? null]),
    [data, metric],
  );

  useEffect(() => {
    if (!elementRef.current) return;
    const chart = echarts.init(elementRef.current, undefined, { renderer: "canvas" });
    chartRef.current = chart;
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(elementRef.current);
    return () => {
      observer.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    chart.setOption({
      animationDurationUpdate: 500,
      backgroundColor: "transparent",
      grid: { left: 58, right: 24, top: 24, bottom: 52 },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross", lineStyle: { color: "#718096", type: "dashed" } },
        backgroundColor: "rgba(18, 23, 32, 0.96)",
        borderColor: "#2b3442",
        textStyle: { color: "#e9eef6", fontFamily: "Consolas, monospace" },
        formatter: (params: unknown) => {
          const list = params as Array<{ value: [number, number | null] }>;
          if (!list.length) return "";
          const [stamp, raw] = list[0].value;
          const time = new Intl.DateTimeFormat("zh-CN", { hour: "2-digit", minute: "2-digit" }).format(stamp);
          const value = raw == null ? "--" : `${meta.unit}${Number(raw).toLocaleString("zh-CN", { maximumFractionDigits: 2 })}${metric === "ctr" || metric === "cvr" ? "%" : ""}`;
          return `<div style="min-width:130px"><div style="color:#8d98a8;margin-bottom:8px">${time}</div><b>${meta.label}　${value}</b></div>`;
        },
      },
      xAxis: {
        type: "time",
        boundaryGap: false,
        axisLine: { lineStyle: { color: "#293241" } },
        axisLabel: { color: "#788496", formatter: "{HH}:{mm}" },
        splitLine: { show: true, lineStyle: { color: "rgba(62, 73, 89, .22)" } },
      },
      yAxis: {
        type: "value",
        scale: true,
        axisLabel: { color: "#788496" },
        splitLine: { lineStyle: { color: "rgba(62, 73, 89, .28)" } },
      },
      dataZoom: [
        { type: "inside", zoomOnMouseWheel: true, moveOnMouseMove: true },
        { type: "slider", height: 16, bottom: 8, borderColor: "transparent", fillerColor: "rgba(88,166,255,.16)", backgroundColor: "rgba(255,255,255,.03)", handleStyle: { color: "#58a6ff" }, textStyle: { color: "transparent" } },
      ],
      series: [{
        name: meta.label,
        type: "line",
        showSymbol: false,
        smooth: 0.2,
        connectNulls: true,
        data: points,
        lineStyle: { color: meta.color, width: 2 },
        itemStyle: { color: meta.color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: `${meta.color}42` },
            { offset: 1, color: `${meta.color}03` },
          ]),
        },
      }],
    }, { notMerge: false, lazyUpdate: true });
  }, [meta, metric, points]);

  return data.length ? <div ref={elementRef} className="intraday-chart" /> : <div className="empty-state">暂无分时数据，等待 Mock 引擎生成</div>;
}

