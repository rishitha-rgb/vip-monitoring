// LoginForm.js
import React from "react";
import { Form, Input, Button, Checkbox } from "antd";
import { UserOutlined, LockOutlined, LoginOutlined } from "@ant-design/icons";

const LoginForm = () => {
  const onFinish = (values) => {
    console.log("Login Success:", values);
  };

  return (
    <Form
      name="login"
      onFinish={onFinish}
      style={{ maxWidth: 400, margin: "auto" }}
      layout="vertical"
    >
      <Form.Item
        name="username"
        rules={[{ required: true, message: "Enter your email or username!" }]}
      >
        <Input prefix={<UserOutlined />} placeholder="Email or Username" />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: "Enter your password!" }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Password" />
      </Form.Item>

      <Form.Item name="remember" valuePropName="checked">
        <Checkbox>Remember this device</Checkbox>
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" icon={<LoginOutlined />} block>
          Login
        </Button>
      </Form.Item>
    </Form>
  );
};

export default LoginForm;
