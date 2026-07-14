import React from 'react';
import { Box, Flex, Button, Container } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

function Navigation({ isAuthenticated, setIsAuthenticated }) {
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  return (
    <Box bg="white" boxShadow="sm" py={4}>
      <Container maxW="container.xl">
        <Flex justify="space-between" align="center">
          <Link to="/" style={{ fontSize: '24px', fontWeight: 'bold' }}>
            📚 Exam RAG Portal
          </Link>
          <Flex gap={4}>
            {isAuthenticated ? (
              <>
                <Button as={Link} to="/dashboard" variant="ghost">Dashboard</Button>
                <Button as={Link} to="/exam/generate" colorScheme="blue">Generate Exam</Button>
                <Button onClick={handleLogout} colorScheme="red" variant="outline">Logout</Button>
              </>
            ) : (
              <>
                <Button as={Link} to="/login" variant="ghost">Login</Button>
                <Button as={Link} to="/register" colorScheme="blue">Register</Button>
              </>
            )}
          </Flex>
        </Flex>
      </Container>
    </Box>
  );
}

export default Navigation;
