import React, { useState } from 'react';
import { Box, Button, FormControl, FormLabel, Input, VStack, Heading, useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Register({ setIsAuthenticated }) {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post('http://localhost:8000/api/v1/auth/register', formData);
      
      toast({ title: 'Registration successful', status: 'success' });
      navigate('/login');
    } catch (error) {
      toast({ title: 'Registration failed', description: error.response?.data?.detail || 'An error occurred', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <VStack spacing={8} maxW="md" mx="auto">
      <Heading>Register</Heading>
      <Box as="form" width="100%" onSubmit={handleRegister}>
        <VStack spacing={4}>
          <FormControl>
            <FormLabel>Email</FormLabel>
            <Input type="email" name="email" value={formData.email} onChange={handleChange} required />
          </FormControl>
          <FormControl>
            <FormLabel>Username</FormLabel>
            <Input name="username" value={formData.username} onChange={handleChange} required />
          </FormControl>
          <FormControl>
            <FormLabel>Password</FormLabel>
            <Input type="password" name="password" value={formData.password} onChange={handleChange} required />
          </FormControl>
          <FormControl>
            <FormLabel>First Name</FormLabel>
            <Input name="first_name" value={formData.first_name} onChange={handleChange} />
          </FormControl>
          <FormControl>
            <FormLabel>Last Name</FormLabel>
            <Input name="last_name" value={formData.last_name} onChange={handleChange} />
          </FormControl>
          <Button type="submit" colorScheme="blue" width="100%" isLoading={loading}>
            Register
          </Button>
        </VStack>
      </Box>
    </VStack>
  );
}

export default Register;
