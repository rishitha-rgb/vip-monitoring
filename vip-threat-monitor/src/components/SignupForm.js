// SignupForm.js
import React from "react";
import { Form, Input, Button, Checkbox } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";

const SignupForm = () => {
  const onFinish = (values) => {
    console.log("Signup Success:", values);
  };

  return (
    <Form
      name="signup"
      onFinish={onFinish}
      style={{ maxWidth: 400, margin: "auto" }}
      layout="vertical"
    >
      <Form.Item
        name="fullname"
        rules={[{ required: true, message: "Enter your full name!" }]}
      >
        <Input prefix={<UserOutlined />} placeholder="Full Name" />
      </Form.Item>

      <Form.Item
        name="email"
        rules={[
          { required: true, type: "email", message: "Enter a valid email!" },
        ]}
      >
        <Input placeholder="Email Address" />
      </Form.Item>

      <Form.Item
        name="username"
        rules={[{ required: true, message: "Choose a username!" }]}
      >
        <Input placeholder="Username" />
      </Form.Item>

      <Form.Item
        name="password"
        rules={[{ required: true, message: "Enter a password!" }]}
      >
        <Input.Password prefix={<LockOutlined />} placeholder="Password" />
      </Form.Item>

      <Form.Item
        name="confirm"
        dependencies={["password"]}
        rules={[
          { required: true, message: "Confirm your password!" },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue("password") === value)
                return Promise.resolve();
              return Promise.reject(new Error("Passwords do not match!"));
            },
          }),
        ]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="Confirm Password"
        />
      </Form.Item>

      <Form.Item
        name="agree"
        valuePropName="checked"
        rules={[{ required: true, message: "Accept terms!" }]}
      >
        <Checkbox>I agree to the Terms of Service and Privacy Policy</Checkbox>
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit" block>
          Create Account
        </Button>
      </Form.Item>
    </Form>
  );
};

export default SignupForm;
