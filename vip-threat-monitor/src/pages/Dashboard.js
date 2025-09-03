// Dashboard.js
import React from "react";
import { Row, Col } from "antd";
import { UserOutlined, WarningOutlined } from "@ant-design/icons";
import DashboardCard from "../components/DashboardCard";

const Dashboard = () => (
  <div style={{ padding: 20 }}>
    <h1 style={{ color: "#fff" }}>Security Dashboard</h1>
    <p style={{ color: "#aaa" }}>
      Real-time monitoring of <b>30 Indian VIPs</b> across major platforms
    </p>

    <Row gutter={16}>
      <Col span={12}>
        <DashboardCard
          title="VIPs Monitored"
          value={30}
          icon={<UserOutlined style={{ fontSize: 32, color: "#00bfff" }} />}
          color="#00bfff"
          footer="Politicians, Celebrities, Business Leaders"
        />
      </Col>
      <Col span={12}>
        <DashboardCard
          title="Active Threats"
          value={287}
          icon={<WarningOutlined style={{ fontSize: 32, color: "#ff4d4f" }} />}
          color="#ff4d4f"
          footer="Detected in last 24 hours"
        />
      </Col>
    </Row>
  </div>
);

export default Dashboard;
