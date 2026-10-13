import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const HelloWorld: React.FC<{ title: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 12 } });
  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });
  const rotate = interpolate(frame, [0, 90], [0, 360]);

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(135deg, #1e3a8a, #9333ea)",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "sans-serif",
      }}
    >
      <div
        style={{
          width: 120,
          height: 120,
          borderRadius: 24,
          background: "#facc15",
          transform: `rotate(${rotate}deg)`,
          marginBottom: 40,
        }}
      />
      <h1
        style={{
          color: "white",
          fontSize: 80,
          margin: 0,
          opacity,
          transform: `scale(${scale})`,
        }}
      >
        {title}
      </h1>
    </AbsoluteFill>
  );
};
