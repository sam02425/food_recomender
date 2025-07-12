// frontend/components/RecommendationEngine.tsx
import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Alert,
  AlertTitle,
  Skeleton,
  Button,
  Chip,
  Box,
  LinearProgress
} from '@mui/material';
import {
  Warning as WarningIcon,
  Speed as SpeedIcon,
  Favorite as FavoriteIcon,
  Security as SecurityIcon,
  CheckCircle as CheckIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import {
  RecommendationRequest,
  RecommendationResponse,
  UnifiedRecommendation,
  UserContext,
  AgentType,
  RiskLevel,
  ProblemPreventionRecommendation
} from '../../types/agents';
// import { useAgentService } from '../hooks/useAgentService';

interface RecommendationEngineProps {
  userContext: UserContext;
  orderDetails?: any;
  requestType?: 'full_recommendation' | 'quick_recommendation' | 'risk_assessment' | 'context_only';
  onRecommendationSelect?: (recommendation: UnifiedRecommendation) => void;
  showAgentDetails?: boolean;
}

export const RecommendationEngine: React.FC<RecommendationEngineProps> = ({
  userContext,
  orderDetails,
  requestType = 'full_recommendation',
  onRecommendationSelect,
  showAgentDetails = false
}) => {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  // const { getRecommendations, submitFeedback } = useAgentService();

  // Load recommendations on mount and when context changes
  useEffect(() => {
    loadRecommendations();
  }, [userContext.user_id, requestType, orderDetails]);

  const loadRecommendations = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const request: RecommendationRequest = {
        user_context: userContext,
        request_type: requestType,
        order_details: orderDetails
      };

      // const result = await getRecommendations(request);
      // setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  }, [userContext, requestType, orderDetails]);

  const handleRecommendationClick = useCallback(async (recommendation: UnifiedRecommendation) => {
    // Submit feedback that user clicked on recommendation
    // await submitFeedback({
    //   agent_type: getAgentTypeFromSource(recommendation.source),
    //   feedback: {
    //     type: 'recommendation_clicked',
    //     accepted: true
    //   }
    // });

    onRecommendationSelect?.(recommendation);
  }, [onRecommendationSelect]);

  const getAgentTypeFromSource = (source: string): AgentType => {
    switch (source) {
      case 'context_intelligence': return AgentType.CONTEXT_INTELLIGENCE;
      case 'preference_learning': return AgentType.PREFERENCE_LEARNING;
      case 'preparation_time': return AgentType.PREPARATION_TIME;
      default: return AgentType.CONTEXT_INTELLIGENCE;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <WarningIcon />;
      case 'medium': return <SpeedIcon />;
      case 'low': return <FavoriteIcon />;
      default: return <CheckIcon />;
    }
  };

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'context_intelligence': return <SpeedIcon />;
      case 'preference_learning': return <FavoriteIcon />;
      case 'preparation_time': return <AccessTimeIcon />;
      default: return <CheckIcon />;
    }
  };

  if (loading) {
    return (
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Getting Recommendations...
          </Typography>
          <LinearProgress sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Skeleton variant="rectangular" height={60} />
            <Skeleton variant="rectangular" height={60} />
            <Skeleton variant="rectangular" height={60} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        <AlertTitle>Error Loading Recommendations</AlertTitle>
        {error}
        <Button onClick={loadRecommendations} sx={{ mt: 1 }}>
          Try Again
        </Button>
      </Alert>
    );
  }

  if (!response || !response.success) {
    return (
      <Alert severity="warning" sx={{ mb: 2 }}>
        <AlertTitle>No Recommendations Available</AlertTitle>
        Unable to generate recommendations at this time.
      </Alert>
    );
  }

  return (
    <Box>
      {/* Main Recommendations */}
      {response.combined_recommendations?.unified_recommendations && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FavoriteIcon color="primary" />
              Recommendations for You
              <Chip
                label={`${response.combined_recommendations.overall_confidence.toFixed(1)}% confident`}
                size="small"
                color="primary"
                variant="outlined"
              />
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {response.combined_recommendations.unified_recommendations.map((rec: UnifiedRecommendation, index: number) => (
                <Card
                  key={index}
                  variant="outlined"
                  sx={{
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'action.hover' },
                    borderLeft: `4px solid`,
                    borderLeftColor: `${getPriorityColor(rec.priority)}.main`
                  }}
                  onClick={() => handleRecommendationClick(rec)}
                >
                  <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      {getPriorityIcon(rec.priority)}
                      <Typography variant="subtitle2" fontWeight="bold">
                        {rec.title}
                      </Typography>
                      <Box sx={{ flexGrow: 1 }} />
                      {getSourceIcon(rec.source)}
                      <Chip
                        label={rec.priority}
                        size="small"
                        color={getPriorityColor(rec.priority) as any}
                        variant="outlined"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {rec.message}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Risk Factors */}
      {response.combined_recommendations?.risk_factors && response.combined_recommendations.risk_factors.length > 0 && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SecurityIcon color="warning" />
              Potential Issues
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {response.combined_recommendations.risk_factors.map((risk: ProblemPreventionRecommendation, index: number) => (
                <Alert key={index} severity={getPriorityColor(risk.priority) as any} variant="outlined">
                  <Typography variant="subtitle2">{risk.message}</Typography>
                </Alert>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Personalization Insights */}
      {response.combined_recommendations?.personalization_insights &&
       response.combined_recommendations.personalization_insights.length > 0 && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FavoriteIcon color="info" />
              Your Ordering Patterns
            </Typography>

            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {response.combined_recommendations.personalization_insights.map((insight: string, index: number) => (
                <Chip
                  key={index}
                  label={insight}
                  size="small"
                  color="info"
                  variant="outlined"
                />
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Agent Details (Debug/Research Mode) */}
      {showAgentDetails && response.agent_results && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Agent Performance Details
            </Typography>

            {Object.entries(response.agent_results).map(([agentName, result]: [string, any]) => (
              <Card key={agentName} variant="outlined" sx={{ mb: 1 }}>
                <CardContent sx={{ py: 1, '&:last-child': { pb: 1 } }}>
                  <Box sx={{ display: 'flex', justifyContent: 'between', alignItems: 'center' }}>
                    <Typography variant="subtitle2" sx={{ textTransform: 'capitalize' }}>
                      {agentName.replace('_', ' ')} Agent
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Chip
                        label={result.success ? 'Success' : 'Failed'}
                        size="small"
                        color={result.success ? 'success' : 'error'}
                        variant="outlined"
                      />
                      <Typography variant="caption">
                        {result.execution_time_ms}ms
                      </Typography>
                      <Typography variant="caption">
                        {(result.confidence * 100).toFixed(0)}% confident
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}

            <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
              Total execution time: {response.orchestrator_metadata.execution_time_ms}ms
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Button
          variant="outlined"
          size="small"
          onClick={loadRecommendations}
        >
          Refresh Recommendations
        </Button>

        {requestType !== 'quick_recommendation' && (
          <Button
            variant="outlined"
            size="small"
            onClick={() => {
              const quickRequest: RecommendationRequest = {
                user_context: userContext,
                request_type: 'quick_recommendation'
              };
              // getRecommendations(quickRequest).then(setResponse);
            }}
          >
            Quick Suggestions
          </Button>
        )}

        {requestType !== 'risk_assessment' && orderDetails && (
          <Button
            variant="outlined"
            size="small"
            onClick={() => {
              const riskRequest: RecommendationRequest = {
                user_context: userContext,
                request_type: 'risk_assessment',
                order_details: orderDetails
              };
              // getRecommendations(riskRequest).then(setResponse);
            }}
          >
            Check Delivery Risk
          </Button>
        )}
      </Box>
    </Box>
  );
};

// Specialized components for different recommendation types
export const QuickRecommendations: React.FC<Omit<RecommendationEngineProps, 'requestType'>> = (props) => (
  <RecommendationEngine {...props} requestType="quick_recommendation" />
);

export const RiskAssessment: React.FC<Omit<RecommendationEngineProps, 'requestType'>> = (props) => (
  <RecommendationEngine {...props} requestType="risk_assessment" />
);

export const ContextualInfo: React.FC<Omit<RecommendationEngineProps, 'requestType'>> = (props) => (
  <RecommendationEngine {...props} requestType="context_only" />
);