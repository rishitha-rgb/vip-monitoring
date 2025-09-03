import React from "react";
import { Menu } from "antd";
import { useNavigate, useLocation } from "react-router-dom";
import {
  DashboardOutlined,
  UserOutlined,
  WarningOutlined,
  TeamOutlined,
  ShieldOutlined,
  BarChartOutlined,
  SettingOutlined,
} from "@ant-design/icons";

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleMenuClick = (e) => {
    // Each key must match a route.
    navigate(`/${e.key === "dashboard" ? "" : e.key}`);
  };

  return (
    <Menu
      mode="inline"
      theme="dark"
      style={{ height: "100vh", width: 220 }}
      selectedKeys={[
        location.pathname === "/"
          ? "dashboard"
          : location.pathname.replace("/", ""),
      ]}
      onClick={handleMenuClick}
    >
      <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
        Dashboard
      </Menu.Item>
      <Menu.Item key="vip-monitoring" icon={<UserOutlined />}>
        VIP Monitoring
      </Menu.Item>
      <Menu.Item key="threat-analysis" icon={<WarningOutlined />}>
        Threat Analysis
      </Menu.Item>
      <Menu.Item key="social-platforms" icon={<TeamOutlined />}>
        Social Platforms
      </Menu.Item>
      <Menu.Item key="user-profiles" icon={<UserOutlined />}>
        User Profiles
      </Menu.Item>
      <Menu.Item key="blocking-center" icon={<ShieldOutlined />}>
        Blocking Center
      </Menu.Item>
      <Menu.Item key="analytics" icon={<BarChartOutlined />}>
        Analytics
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        Settings
      </Menu.Item>
    </Menu>
  );
};

export default Sidebar;
