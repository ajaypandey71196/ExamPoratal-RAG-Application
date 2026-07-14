import React from 'react';
import { Box, Heading, Text, Button, Stack, VStack } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

function Home() {
  const isAuthenticated = !!localStorage.getItem('access_token');

  return (
    <VStack spacing={8} align="stretch">
      <Box textAlign="center" py={12}>
        <Heading as="h1" size="2xl" mb={4}>
          📚 Exam Portal Powered by RAG
        </Heading>
        <Text fontSize="lg" color="gray.600" mb={8}>
          Generate dynamic exams from your documents and internet resources using AI
        </Text>
        <Stack direction="row" spacing={4} justify="center">
          {isAuthenticated ? (
            <>
              <Button as={Link} to="/exam/generate" colorScheme="blue" size="lg">
                Create New Exam
              </Button>
              <Button as={Link} to="/dashboard" variant="outline" size="lg">
                View Exams
              </Button>
            </>
          ) : (
            <>
              <Button as={Link} to="/register" colorScheme="blue" size="lg">
                Get Started
              </Button>
              <Button as={Link} to="/login" variant="outline" size="lg">
                Login
              </Button>
            </>
          )}
        </Stack>
      </Box>

      <Box bg="blue.50" p={8} borderRadius="lg">
        <Heading size="md" mb={4}>Features</Heading>
        <Stack spacing={2}>
          <Text>✅ Upload and process documents</Text>
          <Text>✅ Scrape data from internet sources</Text>
          <Text>✅ AI-powered exam generation</Text>
          <Text>✅ Customizable prompts and models</Text>
          <Text>✅ Share exams with others</Text>
        </Stack>
      </Box>
    </VStack>
  );
}

export default Home;
