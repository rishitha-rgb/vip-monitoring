// DashboardCard.js
import React from "react";
import { Card, Statistic } from "antd";

const DashboardCard = ({ title, value, icon, color, footer }) => (
  <Card
    style={{ borderRadius: 12, backgroundColor: "#141414", color: "#fff" }}
    bodyStyle={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    }}
  >
    <div>{icon}</div>
    <Statistic title={title} value={value} valueStyle={{ color }} />
    {footer && (
      <div style={{ marginTop: 8, fontSize: 12, color: "#aaa" }}>{footer}</div>
    )}
  </Card>
);

export default DashboardCard;
