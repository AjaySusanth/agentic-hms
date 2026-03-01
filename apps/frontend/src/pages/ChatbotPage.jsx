import { useEffect, useMemo, useState } from 'react';
import { MessageCircle, Send } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { ChatbotService } from '../services/api';

const ChatbotPage = () => {
  const [sessionId, setSessionId] = useState(null);
  const [step, setStep] = useState('greeting');
  const [sessionData, setSessionData] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState('');

  const lastBotMessage = useMemo(
    () => [...messages].reverse().find((m) => m.role === 'bot')?.content || '',
    [messages]
  );

  useEffect(() => {
    const initSession = async () => {
      setIsInitializing(true);
      setError('');
      try {
        const response = await ChatbotService.startSession();
        setSessionId(response.session_id);
        setStep(response.step || 'greeting');
        setSessionData(response.session_data || null);
        setMessages([{ role: 'bot', content: response.message || 'Hello!' }]);
      } catch (err) {
        setError(err.message || 'Failed to start chatbot session.');
      } finally {
        setIsInitializing(false);
      }
    };

    initSession();
  }, []);

  const appendUserMessage = (content) => {
    setMessages((prev) => [...prev, { role: 'user', content }]);
  };

  const appendBotMessage = (content) => {
    setMessages((prev) => [...prev, { role: 'bot', content }]);
  };

  const sendPayload = async (payload, displayUserMessage) => {
    if (!sessionId) return;

    setIsLoading(true);
    setError('');

    if (displayUserMessage) {
      appendUserMessage(displayUserMessage);
    }

    try {
      const response = await ChatbotService.sendMessage(sessionId, payload);
      setStep(response.step || step);
      setSessionData(response.session_data || null);
      appendBotMessage(response.message || '');
    } catch (err) {
      setError(err.message || 'Failed to send message.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendText = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setInput('');
    await sendPayload({ message: trimmed }, trimmed);
  };

  const parseDoctorsFromMessage = (text) => {
    const lines = (text || '').split('\n');
    const options = [];

    for (const line of lines) {
      const stripped = line.replace(/\*\*/g, '').trim();
      const match = stripped.match(/^(\d+)\.\s+(.+)$/);
      if (match) {
        options.push({
          value: match[1],
          label: match[2],
        });
      }
    }

    return options;
  };

  const parseDepartmentsFromMessage = (text) => {
    const marker = 'Available departments:';
    const idx = (text || '').indexOf(marker);
    if (idx === -1) return [];

    const after = text.slice(idx + marker.length).split('\n')[0] || '';
    return after
      .split(',')
      .map((d) => d.trim())
      .filter(Boolean)
      .map((d) => ({ value: d, label: d }));
  };

  const quickActions = useMemo(() => {
    if (!step) return [];

    if (step === 'confirm_booking') {
      return [
        {
          label: 'Yes, proceed',
          onClick: () => sendPayload({ message: 'yes' }, 'yes'),
        },
        {
          label: 'No, cancel',
          onClick: () => sendPayload({ message: 'no' }, 'no'),
        },
      ];
    }

    if (step === 'select_hospital' && sessionData?.available_hospitals?.length) {
      return sessionData.available_hospitals.map((hospital, index) => ({
        label: `${index + 1}. ${hospital.name}`,
        onClick: () => sendPayload({ message: String(index + 1) }, String(index + 1)),
      }));
    }

    if (step === 'proxy_registration') {
      const deptOptions = parseDepartmentsFromMessage(lastBotMessage);
      if (deptOptions.length > 0) {
        return [
          {
            label: 'Yes, confirm department',
            onClick: () =>
              sendPayload({ message: 'yes', confirm: 'true' }, 'yes'),
          },
          ...deptOptions.map((option) => ({
            label: option.label,
            onClick: () =>
              sendPayload(
                { message: option.value, department: option.value },
                option.value
              ),
          })),
        ];
      }

      const doctorOptions = parseDoctorsFromMessage(lastBotMessage);
      if (doctorOptions.length > 0) {
        return doctorOptions.map((doctor) => ({
          label: doctor.label,
          onClick: () => sendPayload({ message: doctor.value }, doctor.value),
        }));
      }
    }

    return [];
  }, [lastBotMessage, sessionData, step]);

  const handleRestart = async () => {
    setMessages([]);
    setSessionData(null);
    setStep('greeting');
    setInput('');
    setError('');

    setIsInitializing(true);
    try {
      const response = await ChatbotService.startSession();
      setSessionId(response.session_id);
      setStep(response.step || 'greeting');
      setSessionData(response.session_data || null);
      setMessages([{ role: 'bot', content: response.message || 'Hello!' }]);
    } catch (err) {
      setError(err.message || 'Failed to restart chatbot session.');
    } finally {
      setIsInitializing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="section-header mb-3">
          <div className="section-icon">
            <MessageCircle className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">Healthcare Chatbot</h2>
            <p className="text-sm text-gray-600">Find hospitals and complete registration from a single chat flow.</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <span className="badge badge-primary">Step: {step}</span>
          {sessionId && <span className="badge badge-gray">Session: {String(sessionId).slice(0, 8)}...</span>}
          <button className="btn-ghost ml-auto" onClick={handleRestart} disabled={isLoading || isInitializing}>
            Restart Chat
          </button>
        </div>
      </div>

      {error && <ErrorMessage message={error} onClose={() => setError('')} />}

      <div className="card">
        {isInitializing ? (
          <LoadingSpinner message="Starting chatbot session..." />
        ) : (
          <>
            <div className="max-h-[420px] overflow-y-auto scrollbar-thin space-y-3 pr-1">
              {messages.map((message, idx) => (
                <div
                  key={`${message.role}-${idx}`}
                  className={`rounded-lg p-3 border ${
                    message.role === 'user'
                      ? 'bg-primary-50 border-primary-200 ml-8'
                      : 'bg-gray-50 border-gray-200 mr-8'
                  }`}
                >
                  <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 mb-1">
                    {message.role === 'user' ? 'You' : 'Assistant'}
                  </p>
                  <div className="text-sm text-gray-800 whitespace-pre-wrap">
                    {message.content.split(/(\[.+?\]\(.+?\))/).map((part, i) => {
                      const linkMatch = part.match(/\[(.+?)\]\((.+?)\)/);
                      if (linkMatch) {
                        return (
                          <a
                            key={i}
                            href={linkMatch[2]}
                            className="text-primary-600 hover:underline font-medium break-all"
                            target={linkMatch[2].startsWith('http') ? '_blank' : '_self'}
                            rel="noopener noreferrer"
                          >
                            {linkMatch[1]}
                          </a>
                        );
                      }
                      return part;
                    })}
                  </div>
                </div>
              ))}
            </div>

            {quickActions.length > 0 && (
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">Quick options</p>
                <div className="flex flex-wrap gap-2">
                  {quickActions.map((action, idx) => (
                    <button
                      key={`quick-${idx}`}
                      className="btn-secondary"
                      onClick={action.onClick}
                      disabled={isLoading}
                    >
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleSendText} className="mt-4 flex gap-2">
              <input
                className="input-field"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message"
                disabled={isLoading}
              />
              <button type="submit" className="btn-primary flex items-center gap-2" disabled={isLoading || !input.trim()}>
                <Send className="w-4 h-4" />
                Send
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default ChatbotPage;
