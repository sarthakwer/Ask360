"""Tests for intent routing."""

import pytest
from ask360.ask360_core import answer


def test_trend_intent():
    """Test trend intent routing."""
    questions = [
        "How is yogurt doing at FreshFoods? Show the last 12 months trend.",
        "Show me the monthly trend",
        "How is yogurt doing"
    ]
    for q in questions:
        result = answer(q)
        assert result['intent'] == 'trend'


def test_growth_markets_intent():
    """Test growth_markets intent routing."""
    questions = [
        "Which were the top 3 growth markets for yogurt last year?",
        "Which markets have the fastest growing sales?",
        "top 3 growth markets"
    ]
    for q in questions:
        result = answer(q)
        assert result['intent'] == 'growth_markets'


def test_segment_repeat_intent():
    """Test segment_repeat intent routing."""
    questions = [
        "Among 18–34 vs 35–54, who has higher repeat rate for yogurt?",
        "What is the repeat rate by age segment?",
        "trial vs repeat"
    ]
    for q in questions:
        result = answer(q)
        assert result['intent'] == 'segment_repeat'


def test_occasions_intent():
    """Test occasions intent routing."""
    questions = [
        "What are the top consumption occasions for shelf-stable yogurt?",
        "When do people consume yogurt?",
        "consumption occasions"
    ]
    for q in questions:
        result = answer(q)
        assert result['intent'] == 'occasions'


def test_channel_pack_intent():
    """Test channel_pack intent routing."""
    questions = [
        "In e-commerce vs retail, which channel grew faster for multipack yogurt?",
        "ecommerce single pack growth",
        "which channel grew faster"
    ]
    for q in questions:
        result = answer(q)
        assert result['intent'] == 'channel_pack'


def test_answer_structure():
    """Test that answer() returns expected structure."""
    result = answer("How is yogurt doing?")
    
    assert 'intent' in result
    assert 'text' in result
    assert isinstance(result['text'], list)
    assert len(result['text']) > 0

