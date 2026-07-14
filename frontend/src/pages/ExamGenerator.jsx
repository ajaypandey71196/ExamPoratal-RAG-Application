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
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  Checkbox,
  Spinner,
  useToast,
  Badge,
  Divider,
  SimpleGrid,
  Icon,
  Progress,
  Grid,
  GridItem
} from '@chakra-ui/react';
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function ExamGenerator() {
  const navigate = useNavigate();
  const toast = useToast();
  
  // State management
  const [documents, setDocuments] = useState([]);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [formData, setFormData] = useState({
    topic: '',
    num_questions: 5,
    question_type: 'MCQ',
    difficulty_level: 'medium',
    custom_instructions: '',
    source_preference: 'documents'
  });
  const [llmConfig, setLlmConfig] = useState({
    provider: 'ollama',
    model: 'llama2',
    api_key: '',
    temperature: 0.7,
    max_tokens: 2000
  });
  const [generating, setGenerating] = useState(false);
  const [generatedExam, setGeneratedExam] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const getAuthToken = () => {
    return localStorage.getItem('access_token');
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/list`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setDocuments(response.data.documents?.filter(d => d.processing_status === 'completed') || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const handleFileUpload = async (files) => {
    if (!files.length) return;

    const file = files[0];
    const formDataUpload = new FormData();
    formDataUpload.append('file', file);

    try {
      setUploadProgress(50);
      const response = await axios.post(
        `${API_BASE_URL}/documents/upload`,
        formDataUpload,
        {
          headers: {
            Authorization: `Bearer ${getAuthToken()}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setUploadProgress(100);
      toast({
        title: 'Success',
        description: `Document "${file.name}" uploaded successfully`,
        status: 'success',
        duration: 3
      });
      setSelectedDocuments([...selectedDocuments, response.data.document_id]);
      fetchDocuments();
      setTimeout(() => setUploadProgress(0), 1000);
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: 'Upload Failed',
        description: error.response?.data?.detail || 'Failed to upload document',
        status: 'error',
        duration: 3
      });
      setUploadProgress(0);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const handleGenerateExam = async () => {
    // Validation
    if (!formData.topic.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please enter a topic',
        status: 'error',
        duration: 3
      });
      return;
    }

    if (selectedDocuments.length === 0 && formData.source_preference === 'documents') {
      toast({
        title: 'Validation Error',
        description: 'Please select at least one document or change source preference',
        status: 'error',
        duration: 3
      });
      return;
    }

    if (llmConfig.provider !== 'ollama' && !llmConfig.api_key.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please enter API key for the selected provider',
        status: 'error',
        duration: 3
      });
      return;
    }

    try {
      setGenerating(true);
      const payload = {
        topic: formData.topic,
        num_questions: parseInt(formData.num_questions),
        question_type: formData.question_type,
        difficulty_level: formData.difficulty_level,
        document_ids: selectedDocuments.length > 0 ? selectedDocuments : undefined,
        custom_instructions: formData.custom_instructions || undefined,
        source_preference: formData.source_preference,
        llm_config: {
          provider: llmConfig.provider,
          model: llmConfig.model,
          api_key: llmConfig.api_key || undefined,
          temperature: parseFloat(llmConfig.temperature),
          max_tokens: parseInt(llmConfig.max_tokens)
        }
      };

      const response = await axios.post(`${API_BASE_URL}/exams/generate`, payload, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });

      setGeneratedExam(response.data);
      toast({
        title: 'Success',
        description: `Exam generated successfully in ${response.data.generation_duration_seconds}s`,
        status: 'success',
        duration: 3
      });
    } catch (error) {
      console.error('Generation error:', error);
      toast({
        title: 'Generation Failed',
        description: error.response?.data?.detail || 'Failed to generate exam',
        status: 'error',
        duration: 3
      });
    } finally {
      setGenerating(false);
    }
  };

  if (generatedExam) {
    return (
      <Container maxW="container.lg" py={8}>
        <VStack align="start" spacing={8}>
          {/* Header */}
          <HStack justify="space-between" w="full">
            <VStack align="start" spacing={2}>
              <Heading size="xl">{generatedExam.title}</Heading>
              <HStack spacing={4}>
                <Badge colorScheme="blue" fontSize="md" px={3} py={1}>
                  {generatedExam.num_questions} Questions
                </Badge>
                <Badge colorScheme="purple" fontSize="md" px={3} py={1}>
                  {generatedExam.question_type}
                </Badge>
                <Badge colorScheme="orange" fontSize="md" px={3} py={1}>
                  {generatedExam.difficulty_level}
                </Badge>
              </HStack>
            </VStack>
            <VStack spacing={2}>
              <Button colorScheme="blue" onClick={() => navigate('/dashboard')}>
                Back to Dashboard
              </Button>
              <Button colorScheme="green" variant="outline" onClick={() => setGeneratedExam(null)}>
                Generate Another
              </Button>
            </VStack>
          </HStack>

          <Divider />

          {/* Exam Info */}
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={4} w="full">
            <Card>
              <CardBody>
                <VStack align="start">
                  <Text fontSize="sm" color="gray.600">Provider</Text>
                  <Text fontWeight="bold">{generatedExam.llm_provider}</Text>
                </VStack>
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <VStack align="start">
                  <Text fontSize="sm" color="gray.600">Generation Time</Text>
                  <Text fontWeight="bold">{generatedExam.generation_duration_seconds}s</Text>
                </VStack>
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <VStack align="start">
                  <Text fontSize="sm" color="gray.600">Topic</Text>
                  <Text fontWeight="bold">{generatedExam.topic}</Text>
                </VStack>
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <VStack align="start">
                  <Text fontSize="sm" color="gray.600">Source</Text>
                  <Text fontWeight="bold">{generatedExam.sources?.length || 0} docs</Text>
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>

          <Divider />

          {/* Questions */}
          <VStack align="start" w="full" spacing={6}>
            <Heading size="lg">Questions</Heading>
            {generatedExam.questions?.map((question, idx) => (
              <Card key={idx} w="full">
                <CardBody>
                  <VStack align="start" spacing={3}>
                    <HStack>
                      <Icon as={CheckCircleIcon} color="green.500" />
                      <Heading size="sm">Question {question.question_number}</Heading>
                      <Badge>{question.difficulty_level}</Badge>
                    </HStack>

                    <Text fontWeight="500" fontSize="md">
                      {question.question_text}
                    </Text>

                    {question.options && (
                      <VStack align="start" spacing={2} pl={6}>
                        {Object.entries(question.options).map(([key, value]) => (
                          <HStack key={key} spacing={2}>
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

                    <Box bg="gray.50" p={3} borderRadius="md" w="full">
                      <Text fontSize="sm" fontWeight="bold" mb={1}>
                        Explanation:
                      </Text>
                      <Text fontSize="sm">{question.explanation}</Text>
                    </Box>

                    {question.key_concepts && (
                      <HStack spacing={2} wrap="wrap">
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
            Save & Go to Dashboard
          </Button>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.lg" py={8}>
      <VStack align="start" spacing={8}>
        <Heading size="xl">Generate Exam</Heading>

        <Stack w="full" spacing={8} direction={{ base: 'column', lg: 'row' }}>
          {/* Left Column - Inputs */}
          <VStack align="start" spacing={6} flex={1}>
            {/* Document Selection */}
            <Card w="full">
              <CardHeader>
                <Heading size="md">Upload Documents</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="start" spacing={4} w="full">
                  <Box
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    p={8}
                    border="2px dashed"
                    borderColor={dragOver ? 'blue.500' : 'gray.300'}
                    borderRadius="lg"
                    textAlign="center"
                    cursor="pointer"
                    bg={dragOver ? 'blue.50' : 'gray.50'}
                    w="full"
                    transition="all 0.3s"
                  >
                    <Input
                      type="file"
                      accept=".pdf,.txt,.docx,.xlsx"
                      onChange={(e) => handleFileUpload(e.target.files)}
                      hidden
                      id="file-input"
                    />
                    <Text
                      as="label"
                      htmlFor="file-input"
                      cursor="pointer"
                      fontWeight="600"
                    >
                      📁 Drag and drop files here or click to browse
                    </Text>
                    <Text fontSize="sm" color="gray.600" mt={2}>
                      Supported: PDF, TXT, DOCX, XLSX (Max 50MB)
                    </Text>
                  </Box>

                  {uploadProgress > 0 && (
                    <Box w="full">
                      <Progress value={uploadProgress} />
                      <Text fontSize="sm" mt={2}>{uploadProgress}% uploaded</Text>
                    </Box>
                  )}

                  {/* Selected Documents */}
                  {documents.length > 0 && (
                    <VStack align="start" w="full">
                      <Text fontWeight="bold">Available Documents:</Text>
                      {documents.map((doc) => (
                        <HStack key={doc.id} spacing={2} w="full">
                          <Checkbox
                            isChecked={selectedDocuments.includes(doc.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDocuments([...selectedDocuments, doc.id]);
                              } else {
                                setSelectedDocuments(selectedDocuments.filter(id => id !== doc.id));
                              }
                            }}
                          />
                          <VStack align="start" spacing={0} flex={1}>
                            <Text fontSize="sm" fontWeight="500">{doc.file_name}</Text>
                            <Text fontSize="xs" color="gray.600">
                              {doc.total_chunks} chunks • {(doc.file_size_bytes / 1024).toFixed(1)} KB
                            </Text>
                          </VStack>
                        </HStack>
                      ))}
                    </VStack>
                  )}
                </VStack>
              </CardBody>
            </Card>

            {/* Exam Configuration */}
            <Card w="full">
              <CardHeader>
                <Heading size="md">Exam Configuration</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="start" spacing={4} w="full">
                  <FormControl>
                    <FormLabel>Topic / Subject</FormLabel>
                    <Input
                      placeholder="e.g., Machine Learning, Python Programming"
                      value={formData.topic}
                      onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Number of Questions</FormLabel>
                    <Input
                      type="number"
                      min="1"
                      max="50"
                      value={formData.num_questions}
                      onChange={(e) => setFormData({ ...formData, num_questions: e.target.value })}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Question Type</FormLabel>
                    <Select
                      value={formData.question_type}
                      onChange={(e) => setFormData({ ...formData, question_type: e.target.value })}
                    >
                      <option value="MCQ">Multiple Choice (MCQ)</option>
                      <option value="SHORT_ANSWER">Short Answer</option>
                      <option value="ESSAY">Essay</option>
                      <option value="MIXED">Mixed</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Difficulty Level</FormLabel>
                    <Select
                      value={formData.difficulty_level}
                      onChange={(e) => setFormData({ ...formData, difficulty_level: e.target.value })}
                    >
                      <option value="easy">Easy</option>
                      <option value="medium">Medium</option>
                      <option value="hard">Hard</option>
                      <option value="mixed">Mixed</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Source Preference</FormLabel>
                    <Select
                      value={formData.source_preference}
                      onChange={(e) => setFormData({ ...formData, source_preference: e.target.value })}
                    >
                      <option value="documents">My Documents</option>
                      <option value="internet">Internet</option>
                      <option value="both">Both</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Custom Instructions (Optional)</FormLabel>
                    <Textarea
                      placeholder="Add any special instructions for exam generation..."
                      rows={3}
                      value={formData.custom_instructions}
                      onChange={(e) => setFormData({ ...formData, custom_instructions: e.target.value })}
                    />
                  </FormControl>
                </VStack>
              </CardBody>
            </Card>
          </VStack>

          {/* Right Column - LLM Config */}
          <VStack align="start" spacing={6} flex={1}>
            <Card w="full">
              <CardHeader>
                <Heading size="md">LLM Configuration</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="start" spacing={4} w="full">
                  <FormControl>
                    <FormLabel>LLM Provider</FormLabel>
                    <Select
                      value={llmConfig.provider}
                      onChange={(e) => setLlmConfig({ ...llmConfig, provider: e.target.value })}
                    >
                      <option value="ollama">Ollama (Local - Free)</option>
                      <option value="openai">OpenAI (GPT-3.5/GPT-4)</option>
                      <option value="cohere">Cohere</option>
                      <option value="huggingface">HuggingFace</option>
                    </Select>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Model</FormLabel>
                    <Input
                      placeholder={
                        llmConfig.provider === 'ollama'
                          ? 'llama2'
                          : llmConfig.provider === 'openai'
                          ? 'gpt-3.5-turbo'
                          : 'command-large'
                      }
                      value={llmConfig.model}
                      onChange={(e) => setLlmConfig({ ...llmConfig, model: e.target.value })}
                    />
                  </FormControl>

                  {llmConfig.provider !== 'ollama' && (
                    <FormControl>
                      <FormLabel>API Key</FormLabel>
                      <Input
                        type="password"
                        placeholder="Your API key"
                        value={llmConfig.api_key}
                        onChange={(e) => setLlmConfig({ ...llmConfig, api_key: e.target.value })}
                      />
                    </FormControl>
                  )}

                  <FormControl>
                    <FormLabel>Temperature</FormLabel>
                    <Input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={llmConfig.temperature}
                      onChange={(e) => setLlmConfig({ ...llmConfig, temperature: e.target.value })}
                    />
                    <Text fontSize="xs" color="gray.600" mt={1}>
                      Lower = more focused, Higher = more creative
                    </Text>
                  </FormControl>

                  <FormControl>
                    <FormLabel>Max Tokens</FormLabel>
                    <Input
                      type="number"
                      min="500"
                      max="4000"
                      step="100"
                      value={llmConfig.max_tokens}
                      onChange={(e) => setLlmConfig({ ...llmConfig, max_tokens: e.target.value })}
                    />
                  </FormControl>

                  <Divider />

                  <Button
                    colorScheme="blue"
                    size="lg"
                    w="full"
                    isLoading={generating}
                    onClick={handleGenerateExam}
                    disabled={generating || !formData.topic}
                  >
                    {generating ? 'Generating Exam...' : 'Generate Exam'}
                  </Button>

                  <Button
                    variant="outline"
                    w="full"
                    onClick={() => navigate('/dashboard')}
                    disabled={generating}
                  >
                    Cancel
                  </Button>
                </VStack>
              </CardBody>
            </Card>

            {/* Info Box */}
            <Card w="full" bg="blue.50" borderColor="blue.200" borderWidth={1}>
              <CardBody>
                <VStack align="start" spacing={2}>
                  <Text fontSize="sm" fontWeight="bold">💡 Tips:</Text>
                  <Text fontSize="xs">• Ollama is free but requires local setup</Text>
                  <Text fontSize="xs">• OpenAI provides best quality (paid)</Text>
                  <Text fontSize="xs">• Upload documents for better context</Text>
                  <Text fontSize="xs">• Generation takes 30-60 seconds</Text>
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </Stack>
      </VStack>
    </Container>
  );
}

export default ExamGenerator;
