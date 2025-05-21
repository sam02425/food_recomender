import React, { useEffect, useRef, useState } from 'react';
import Webcam from 'react-webcam';
import * as faceapi from 'face-api.js';
import { useExperiment } from '../context/ExperimentContext';

const expressionMap = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprised: '😲',
  disgusted: '🤢',
  fearful: '😨',
  neutral: '😐',
};

const getDominantExpression = (expressions) => {
  if (!expressions) return 'neutral';
  let max = 0;
  let dominant = 'neutral';
  Object.entries(expressions).forEach(([exp, value]) => {
    if (value > max) {
      max = value;
      dominant = exp;
    }
  });
  return dominant;
};

const FaceMoodCapture = ({ step }) => {
  const webcamRef = useRef(null);
  const [mood, setMoodState] = useState('neutral');
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const { setMood } = useExperiment();

  useEffect(() => {
    const loadModels = async () => {
      const MODEL_URL = '/models';
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
        faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
      ]);
      setModelsLoaded(true);
    };
    loadModels();
  }, []);

  useEffect(() => {
    let interval;
    if (modelsLoaded) {
      interval = setInterval(async () => {
        if (
          webcamRef.current &&
          webcamRef.current.video &&
          webcamRef.current.video.readyState === 4
        ) {
          const detections = await faceapi.detectSingleFace(
            webcamRef.current.video,
            new faceapi.TinyFaceDetectorOptions()
          ).withFaceExpressions();
          const dominant = getDominantExpression(detections?.expressions);
          setMoodState(dominant);
          setMood(step, dominant);
        }
      }, 1000); // Check every second
    }
    return () => clearInterval(interval);
  }, [modelsLoaded, step, setMood]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: 16 }}>
      <div style={{ width: 160, height: 120, borderRadius: 8, overflow: 'hidden', border: '1px solid #ccc' }}>
        <Webcam
          ref={webcamRef}
          audio={false}
          screenshotFormat="image/jpeg"
          width={160}
          height={120}
        />
      </div>
      <div style={{ marginTop: 8, fontSize: 24 }}>
        Mood: {expressionMap[mood] || '😐'} <span style={{ fontSize: 16 }}>({mood})</span>
      </div>
    </div>
  );
};

export default FaceMoodCapture;