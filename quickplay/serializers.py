from rest_framework import serializers

class QuestionSerializer(serializers.Serializer):
    """
    Serializer for question data returned by the OpenAI service.
    Handles validation and formatting of question data for API responses.
    """
    id = serializers.CharField(read_only=True)
    question = serializers.CharField(max_length=150)
    options = serializers.ListField(
        child=serializers.CharField(max_length=25),
        min_length=4,
        max_length=4
    )
    correct_answer = serializers.CharField(max_length=25)
    explanation = serializers.CharField(max_length=200)
    category = serializers.CharField(max_length=50, default='logical_reasoning')
    is_ai_generated = serializers.BooleanField(default=True)

    def validate(self, data):
        """
        Perform cross-field validation to ensure data consistency.
        """
        if data['correct_answer'] not in data['options']:
            raise serializers.ValidationError(
                "The correct answer must be one of the provided options"
            )
            
        if len(data['options']) != 4:
            raise serializers.ValidationError(
                "Exactly 4 options must be provided"
            )
            
        return data