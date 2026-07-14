import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  Spinner,
  useToast,
  Badge,
  Icon,
  SimpleGrid,
  Box,
  Divider
} from '@chakra-ui/react';
import { CheckCircleIcon, ArrowBackIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function ExamView() {
  const { examId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [exam, setExam] = useState(null);
  const [loading, setLoading] = useState(true);

  const getAuthToken = () => {
    return localStorage.getItem('access_token');
  };

  useEffect(() => {
    fetchExam();
  }, [examId]);

  const fetchExam = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/exams/${examId}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setExam(response.data);
    } catch (error) {
      console.error('Error fetching exam:', error);
      toast({
        title: 'Error',
        description: 'Failed to load exam',
        status: 'error',
        duration: 3
      });
      setTimeout(() => navigate('/dashboard'), 2000);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container maxW="container.lg" py={8}>
        <VStack spacing={4}>
          <Spinner size="lg" />
          <Text>Loading exam...</Text>
        </VStack>
      </Container>
    );
  }

  if (!exam) {
    return (
      <Container maxW="container.lg" py={8}>
        <VStack spacing={4}>
          <Text>Exam not found</Text>
          <Button onClick={() => navigate('/dashboard')}>Back to Dashboard</Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.lg" py={8}>
      <VStack align="start" spacing={8}>
        {/* Header */}
        <HStack w="full" justify="space-between">
          <HStack>
            <Button
              leftIcon={<ArrowBackIcon />}
              variant="ghost"
              onClick={() => navigate('/dashboard')}
            >
              Back
            </Button>
          </HStack>
          <VStack align="end" spacing={1}>
            <Heading size="lg">{exam.title}</Heading>
            <HStack spacing={2}>
              <Badge colorScheme={exam.is_published ? 'green' : 'gray'}>
                {exam.is_published ? 'Published' : 'Draft'}
              </Badge>
              {exam.is_shared && (
                <Badge colorScheme="blue">Shared</Badge>
              )}
            </HStack>
          </VStack>
        </HStack>

        <Divider />

        {/* Info Cards */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} w="full">
          <Card>
            <CardBody>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.600" fontWeight="bold">TOPIC</Text>
                <Text fontWeight="500">{exam.topic}</Text>
              </VStack>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.600" fontWeight="bold">QUESTIONS</Text>
                <Text fontWeight="500">{exam.num_questions}</Text>
              </VStack>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.600" fontWeight="bold">TYPE</Text>
                <Text fontWeight="500">{exam.question_type}</Text>
              </VStack>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.600" fontWeight="bold">DIFFICULTY</Text>
                <Text fontWeight="500">{exam.difficulty_level}</Text>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        <Divider />

        {/* Questions */}
        <VStack align="start" w="full" spacing={6}>
          <Heading size="md">Questions</Heading>
          {exam.questions?.map((question, idx) => (
            <Card key={idx} w="full">
              <CardBody>
                <VStack align="start" spacing={3}>
                  <HStack>
                    <Icon as={CheckCircleIcon} color="green.500" />
                    <Heading size="sm">Q{question.question_number}</Heading>
                    <Badge colorScheme="purple">{question.difficulty_level}</Badge>
                  </HStack>

                  <Text fontWeight="500" fontSize="md">
                    {question.question_text}
                  </Text>

                  {question.options && (
                    <VStack align="start" spacing={2} pl={6} w="full">
                      {Object.entries(question.options).map(([key, value]) => (
                        <HStack key={key} spacing={2} w="full">
                          <Badge
                            colorScheme={key === question.correct_answer ? 'green' : 'gray'}
                            minW="40px"
                          >
                            {key}
                          </Badge>
                          <Text>{value}</Text>
                        </HStack>
                      ))}
                    </VStack>
                  )}

                  <Box bg="gray.50" p={4} borderRadius="md" w="full" borderLeft="4px" borderColor="blue.500">
                    <Text fontSize="sm" fontWeight="bold" mb={2}>
                      Explanation:
                    </Text>
                    <Text fontSize="sm">{question.explanation}</Text>
                  </Box>

                  {question.key_concepts && (
                    <HStack spacing={2} wrap="wrap" w="full">
                      <Text fontSize="sm" fontWeight="bold">Concepts:</Text>
                      {question.key_concepts.split(',').map((concept, i) => (
                        <Badge key={i} colorScheme="blue" variant="subtle">
                          {concept.trim()}
                        </Badge>
                      ))}
                    </HStack>
                  )}
                </VStack>
              </CardBody>
            </Card>
          ))}
        </VStack>

        <Button
          colorScheme="blue"
          size="lg"
          w="full"
          onClick={() => navigate('/dashboard')}
        >
          Back to Dashboard
        </Button>
      </VStack>
    </Container>
  );
}

export default ExamView;
