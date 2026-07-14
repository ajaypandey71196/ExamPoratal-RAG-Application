import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Stack,
  HStack,
  VStack,
  Badge,
  Spinner,
  useToast,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  useDisclosure
} from '@chakra-ui/react';
import { DeleteIcon, DownloadIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function Dashboard() {
  const navigate = useNavigate();
  const toast = useToast();
  const [documents, setDocuments] = useState([]);
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const getAuthToken = () => {
    return localStorage.getItem('access_token');
  };

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/list`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch documents',
        status: 'error',
        duration: 3
      });
    }
  };

  const fetchExams = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/exams/`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setExams(response.data.exams || []);
    } catch (error) {
      console.error('Error fetching exams:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch exams',
        status: 'error',
        duration: 3
      });
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDocuments(), fetchExams()]);
      setLoading(false);
    };
    loadData();
  }, []);

  const handleDeleteDocument = async (docId) => {
    try {
      await axios.delete(`${API_BASE_URL}/documents/${docId}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      toast({
        title: 'Success',
        description: 'Document deleted successfully',
        status: 'success',
        duration: 3
      });
      setDocuments(documents.filter(d => d.id !== docId));
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete document',
        status: 'error',
        duration: 3
      });
    }
  };

  const handleDeleteExam = async (examId) => {
    try {
      await axios.delete(`${API_BASE_URL}/exams/${examId}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      toast({
        title: 'Success',
        description: 'Exam deleted successfully',
        status: 'success',
        duration: 3
      });
      setExams(exams.filter(e => e.id !== examId));
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete exam',
        status: 'error',
        duration: 3
      });
    }
  };

  const handleConfirmDelete = async () => {
    if (deleteTarget.type === 'document') {
      await handleDeleteDocument(deleteTarget.id);
    } else if (deleteTarget.type === 'exam') {
      await handleDeleteExam(deleteTarget.id);
    }
    setDeleteTarget(null);
    onClose();
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    if (status === 'completed') return 'green';
    if (status === 'processing') return 'yellow';
    return 'red';
  };

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="lg" />
          <Text>Loading dashboard...</Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      {/* Header */}
      <VStack align="start" mb={8}>
        <Heading size="xl">Dashboard</Heading>
        <Text color="gray.600">Manage your documents and exams</Text>
      </VStack>

      {/* Stats */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Total Documents</StatLabel>
              <StatNumber>{documents.length}</StatNumber>
            </Stat>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Total Exams</StatLabel>
              <StatNumber>{exams.length}</StatNumber>
            </Stat>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>Questions Generated</StatLabel>
              <StatNumber>
                {exams.reduce((sum, exam) => sum + (exam.num_questions || 0), 0)}
              </StatNumber>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Action Buttons */}
      <HStack mb={8} spacing={4}>
        <Button
          colorScheme="blue"
          size="lg"
          onClick={() => navigate('/exam-generator')}
        >
          Generate New Exam
        </Button>
      </HStack>

      {/* Documents Section */}
      <VStack align="start" mb={12} w="full">
        <Heading size="md" mb={4}>Your Documents ({documents.length})</Heading>
        
        {documents.length === 0 ? (
          <Card w="full">
            <CardBody>
              <Text color="gray.500" textAlign="center" py={8}>
                No documents uploaded yet. Upload a document to get started.
              </Text>
            </CardBody>
          </Card>
        ) : (
          <Stack w="full" spacing={4}>
            {documents.map((doc) => (
              <Card key={doc.id}>
                <CardBody>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={2} flex={1}>
                      <HStack>
                        <Heading size="sm">{doc.file_name}</Heading>
                        <Badge colorScheme={getStatusColor(doc.processing_status)}>
                          {doc.processing_status}
                        </Badge>
                      </HStack>
                      <HStack spacing={4} fontSize="sm" color="gray.600">
                        <Text>Size: {(doc.file_size_bytes / 1024).toFixed(2)} KB</Text>
                        <Text>Chunks: {doc.total_chunks}</Text>
                        <Text>Type: {doc.file_type?.toUpperCase()}</Text>
                      </HStack>
                      <Text fontSize="xs" color="gray.500">
                        Uploaded: {formatDate(doc.upload_date)}
                      </Text>
                    </VStack>
                    <HStack>
                      <Button
                        size="sm"
                        leftIcon={<DeleteIcon />}
                        colorScheme="red"
                        variant="ghost"
                        onClick={() => {
                          setDeleteTarget({ id: doc.id, type: 'document', name: doc.file_name });
                          onOpen();
                        }}
                      >
                        Delete
                      </Button>
                    </HStack>
                  </HStack>
                </CardBody>
              </Card>
            ))}
          </Stack>
        )}
      </VStack>

      {/* Exams Section */}
      <VStack align="start" mb={12} w="full">
        <Heading size="md" mb={4}>Your Exams ({exams.length})</Heading>
        
        {exams.length === 0 ? (
          <Card w="full">
            <CardBody>
              <Text color="gray.500" textAlign="center" py={8}>
                No exams generated yet. Generate an exam to get started.
              </Text>
            </CardBody>
          </Card>
        ) : (
          <Stack w="full" spacing={4}>
            {exams.map((exam) => (
              <Card key={exam.id}>
                <CardBody>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={2} flex={1}>
                      <HStack>
                        <Heading size="sm">{exam.title}</Heading>
                        <Badge colorScheme={exam.is_published ? 'green' : 'gray'}>
                          {exam.is_published ? 'Published' : 'Draft'}
                        </Badge>
                        {exam.is_shared && (
                          <Badge colorScheme="blue">Shared</Badge>
                        )}
                      </HStack>
                      <HStack spacing={4} fontSize="sm" color="gray.600">
                        <Text>Questions: {exam.num_questions}</Text>
                        <Text>Type: {exam.question_type}</Text>
                        <Text>Difficulty: {exam.difficulty_level}</Text>
                      </HStack>
                      <HStack spacing={4} fontSize="xs" color="gray.500">
                        <Text>Provider: {exam.llm_provider}</Text>
                        <Text>Generation Time: {exam.generation_duration_seconds}s</Text>
                        <Text>Created: {formatDate(exam.created_at)}</Text>
                      </HStack>
                    </VStack>
                    <HStack>
                      <Button
                        size="sm"
                        leftIcon={<DownloadIcon />}
                        colorScheme="blue"
                        variant="ghost"
                        onClick={() => navigate(`/exam-view/${exam.id}`)}
                      >
                        View
                      </Button>
                      <Button
                        size="sm"
                        leftIcon={<DeleteIcon />}
                        colorScheme="red"
                        variant="ghost"
                        onClick={() => {
                          setDeleteTarget({ id: exam.id, type: 'exam', name: exam.title });
                          onOpen();
                        }}
                      >
                        Delete
                      </Button>
                    </HStack>
                  </HStack>
                </CardBody>
              </Card>
            ))}
          </Stack>
        )}
      </VStack>

      {/* Delete Confirmation Dialog */}
      <AlertDialog isOpen={isOpen} onClose={onClose}>
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete {deleteTarget?.type}
            </AlertDialogHeader>
            <AlertDialogBody>
              Are you sure you want to delete "{deleteTarget?.name}"? This action cannot be undone.
            </AlertDialogBody>
            <AlertDialogFooter>
              <Button onClick={onClose}>Cancel</Button>
              <Button
                colorScheme="red"
                onClick={handleConfirmDelete}
                ml={3}
              >
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </Container>
  );
}

export default Dashboard;
