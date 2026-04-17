"""
Tests for activity signup and unregister endpoints.
"""
import pytest


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "newstudent@mergington.edu" in response.json()["message"]
        assert "Chess Club" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        response = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added by fetching activities
        activities = client.get("/activities").json()
        programming_class = activities["Programming Class"]
        assert email in programming_class["participants"]

    def test_signup_multiple_different_students(self, client):
        """Test that multiple students can sign up for the same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity = "Tennis Club"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email1}")
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(f"/activities/{activity}/signup?email={email2}")
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities = client.get("/activities").json()
        assert email1 in activities[activity]["participants"]
        assert email2 in activities[activity]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup by same email returns 400"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_same_student_different_activities(self, client):
        """Test that same student can sign up for different activities"""
        email = "multiactivity@mergington.edu"
        
        # Sign up for two different activities
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify in both activities
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive"""
        email = "student@mergington.edu"
        
        # Correct case
        response_correct = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response_correct.status_code == 200
        
        # Wrong case - should be 404
        response_wrong = client.post(
            f"/activities/chess club/signup?email={email}"
        )
        assert response_wrong.status_code == 404

    def test_signup_response_structure(self, client):
        """Test that signup response has correct JSON structure"""
        response = client.post(
            "/activities/Gym Class/signup?email=structure_test@mergington.edu"
        )
        
        json_response = response.json()
        assert "message" in json_response
        assert isinstance(json_response["message"], str)


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup"""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]
        assert "Chess Club" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        
        # Verify participant is in activity before unregister
        activities_before = client.get("/activities").json()
        assert email in activities_before["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_nonexistent_participant_returns_400(self, client):
        """Test that unregistering non-existent participant returns 400"""
        response = client.delete(
            "/activities/Chess Club/signup?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_preserves_other_participants(self, client):
        """Test that unregistering one participant doesn't affect others"""
        activity = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        email_to_keep = "daniel@mergington.edu"
        
        # Get initial participant count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[activity]["participants"])
        
        # Unregister one participant
        response = client.delete(
            f"/activities/{activity}/signup?email={email_to_remove}"
        )
        assert response.status_code == 200
        
        # Verify the right person was removed and others remain
        activities_after = client.get("/activities").json()
        assert len(activities_after[activity]["participants"]) == initial_count - 1
        assert email_to_remove not in activities_after[activity]["participants"]
        assert email_to_keep in activities_after[activity]["participants"]

    def test_unregister_response_structure(self, client):
        """Test that unregister response has correct JSON structure"""
        email = "sophia@mergington.edu"  # In Programming Class
        
        response = client.delete(
            f"/activities/Programming Class/signup?email={email}"
        )
        
        json_response = response.json()
        assert "message" in json_response
        assert isinstance(json_response["message"], str)


class TestSignupUnregisterIntegration:
    """Integration tests for signup and unregister workflows"""

    def test_signup_then_unregister(self, client):
        """Test signup followed by unregister"""
        email = "tempstudent@mergington.edu"
        activity = "Music Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_signup_unregister_signup_cycle(self, client):
        """Test that a student can signup, unregister, and signup again"""
        email = "cyclestudent@mergington.edu"
        activity = "Art Class"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Second signup (should succeed)
        response3 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

    def test_cannot_unregister_twice(self, client):
        """Test that unregistering the same participant twice fails"""
        email = "tempstudent@mergington.edu"
        activity = "Dance Club"
        
        # Create the activity and add the participant
        from src.app import activities
        activities[activity] = {
            "description": "Learn various dance styles",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": [email]
        }
        
        # First unregister should succeed
        response1 = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"].lower()
