import React, { useState, useEffect } from 'react';

const QuestionDisplay = ({ questionData, onAnswerSubmit, isDisabled = false }) => {
  const [shuffledAnswers, setShuffledAnswers] = useState([]);
  
  useEffect(() => {
    if (questionData?.is_ai_generated) {
      // For AI questions, use options array
      const options = [
        questionData.option_1,
        questionData.option_2,
        questionData.option_3,
        questionData.option_4
      ];
      setShuffledAnswers(options.sort(() => Math.random() - 0.5));
    }
  }, [questionData]);

  if (!questionData) {
    return null;
  }

  const categoryMap = {
    'logical_reasoning': 'Logical Reasoning',
    'verbal_linguistic': 'Verbal Linguistic',
    'spatial_reasoning': 'Spatial Reasoning',
    'critical_thinking': 'Critical Thinking',
    'ai_generated': 'AI Generated'
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="mb-6">
        <span className={`question-category category-${questionData.category?.toLowerCase()}`}>
          {categoryMap[questionData.category] || questionData.category}
        </span>
      </div>
      
      <h2 id="questionText" className="text-2xl font-bold text-white mb-8">
        {questionData.question_text}
      </h2>
      
      <div id="options" className="grid grid-cols-2 gap-4">
        {shuffledAnswers.map((answer, index) => (
          <button
            key={index}
            onClick={() => !isDisabled && onAnswerSubmit(answer)}
            disabled={isDisabled}
            className={`option-button bg-white text-[#009fdc] font-bold py-3 px-6 
                      ${index === 0 || index === 2 ? 'rounded-r' : 'rounded-l'} 
                      hover:bg-gray-100 transition-all duration-300
                      disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {answer}
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuestionDisplay;