-- Initialize the chatbot database
CREATE DATABASE chatbot_db;

-- Connect to the chatbot database
\c chatbot_db;

-- Create the message_logs table
CREATE TABLE IF NOT EXISTS message_logs (
    id SERIAL PRIMARY KEY,
    user_query TEXT NOT NULL,
    refined_query TEXT NOT NULL,
    answer TEXT NOT NULL,
    conversation_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_message_logs_timestamp ON message_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_message_logs_conversation_id ON message_logs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_logs_user_query ON message_logs USING gin(to_tsvector('english', user_query));

-- Insert some sample data for testing
INSERT INTO message_logs (user_query, refined_query, answer, conversation_id) VALUES
('What are your business hours?', 'What are the business hours for customer support?', 'We are open Monday through Friday from 9:00 AM to 6:00 PM EST. We are closed on weekends and major holidays.', 'test-conv-1'),
('How do I reset my password?', 'How can I reset my account password?', 'Go to the login page and click "Forgot Password". Enter your email address and we''ll send you a reset link within 5 minutes.', 'test-conv-2'),
('Do you offer free trials?', 'Do you provide free trial periods for your services?', 'Yes! We offer a 14-day free trial for all our products. No credit card required to start your trial.', 'test-conv-3');

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chatbot;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chatbot;