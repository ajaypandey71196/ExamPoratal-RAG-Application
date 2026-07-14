import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Box, Container } from '@chakra-ui/react';

import Navigation from './components/Navigation';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ExamGenerator from './pages/ExamGenerator';
import ExamView from './pages/ExamView';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('access_token'));

  return (
    <Router>
      <Box minH="100vh" bg="gray.50">
        <Navigation isAuthenticated={isAuthenticated} setIsAuthenticated={setIsAuthenticated} />
        <Container maxW="container.xl" py={8}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
            <Route path="/register" element={<Register setIsAuthenticated={setIsAuthenticated} />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/exam-generator" element={<ExamGenerator />} />
            <Route path="/exam-view/:examId" element={<ExamView />} />
          </Routes>
        </Container>
      </Box>
    </Router>
  );
}

export default App;
