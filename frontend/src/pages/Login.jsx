import React, { useState } from 'react';
import { Box, Button, FormControl, FormLabel, Input, VStack, Heading, useToast } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Login({ setIsAuthenticated }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
        email,
        password
      });

      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user_id', response.data.user_id);

      toast({ title: 'Login successful', status: 'success' });
      setIsAuthenticated(true);
      navigate('/dashboard');
    } catch (error) {
      toast({ title: 'Login failed', description: error.response?.data?.detail || 'An error occurred', status: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <VStack spacing={8} maxW="md" mx="auto">
      <Heading>Login</Heading>
      <Box as="form" width="100%" onSubmit={handleLogin}>
        <VStack spacing={4}>
          <FormControl>
            <FormLabel>Email</FormLabel>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </FormControl>
          <FormControl>
            <FormLabel>Password</FormLabel>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </FormControl>
          <Button type="submit" colorScheme="blue" width="100%" isLoading={loading}>
            Login
          </Button>
        </VStack>
      </Box>
    </VStack>
  );
}

export default Login;
