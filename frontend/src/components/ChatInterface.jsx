import React, { useState } from 'react';
import { Box, TextField, Button, Typography, List, ListItem, ListItemText, Paper } from '@mui/material';
import axios from 'axios';

const ChatInterface = () => {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim()) return;

    const userMessage = { sender: 'User', text: question };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setQuestion('');

    try {
      const response = await axios.post('http://localhost:5000/query', {
        question: question,
      });

      const botMessage = { sender: 'Assistant', text: response.data.answer };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error('Error fetching response:', error);
      const errorMessage = { sender: 'Assistant', text: 'Sorry, something went wrong. Please try again.' };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        backgroundColor: '#f5f5f5',
        padding: 2,
      }}
    >
      <Paper elevation={3} sx={{ width: '100%', maxWidth: 600, padding: 2 }}>
        <Typography variant="h4" align="center" gutterBottom>
          Confluence Knowledge Assistant
        </Typography>

        <List sx={{ maxHeight: '60vh', overflow: 'auto' }}>
          {messages.map((msg, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={msg.sender}
                secondary={msg.text}
                primaryTypographyProps={{ fontWeight: 'bold' }}
              />
            </ListItem>
          ))}
          {loading && (
            <ListItem>
              <ListItemText primary="Assistant" secondary="Typing..." primaryTypographyProps={{ fontWeight: 'bold' }} />
            </ListItem>
          )}
        </List>

        <Box sx={{ display: 'flex', marginTop: 2 }}>
          <TextField
            label="Your Question"
            variant="outlined"
            fullWidth
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <Button variant="contained" color="primary" sx={{ marginLeft: 1 }} onClick={handleSend} disabled={loading}>
            Send
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatInterface;
