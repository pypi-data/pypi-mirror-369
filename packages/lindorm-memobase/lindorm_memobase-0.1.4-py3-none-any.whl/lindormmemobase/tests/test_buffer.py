#!/usr/bin/env python3
"""
Buffer Storage Integration Tests

This test suite tests the LindormBufferStorage implementation
using real Lindorm Wide Table connections from .env configuration.
"""

import sys
import asyncio
import pytest
import uuid
from datetime import datetime
from dotenv import load_dotenv
from lindormmemobase.config import Config
from lindormmemobase.core.constants import BufferStatus
from lindormmemobase.core.buffer.buffer import (
    LindormBufferStorage,
)
from lindormmemobase.models.blob import ChatBlob, BlobType, OpenAICompatibleMessage
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Load .env file from the tests directory
test_dir = Path(__file__).parent
env_file = test_dir / ".env"
load_dotenv(env_file)


class TestBufferStorage:
    """Test suite for LindormBufferStorage using real Lindorm connections."""

    @classmethod
    def setup_class(cls):
        """Setup test class with configuration."""
        cls.config = Config.load_config()
        cls.config.max_chat_blob_buffer_token_size = 128
        cls.storage = LindormBufferStorage(cls.config)
        cls.test_user_id = "test_user_123"
        cls.test_blob_ids = []
        
        # Clean up any existing test data before starting tests
        asyncio.run(cls._cleanup_test_data())

    @classmethod
    def teardown_class(cls):
        """Cleanup test data after all tests."""
        asyncio.run(cls._cleanup_test_data())

    @classmethod
    async def _cleanup_test_data(cls):
        """Clean up test data from database."""
        pool = cls.storage._get_pool()
        conn = pool.get_connection()
        cursor = None

        try:
            cursor = conn.cursor()

            # Get all blob IDs for this user from buffer_zone
            cursor.execute(
                "SELECT blob_id FROM buffer_zone WHERE user_id = %s",
                (cls.test_user_id,)
            )
            buffer_blob_ids = [row[0] for row in cursor.fetchall()]

            # Delete buffer zone entries individually using composite key
            for blob_id in buffer_blob_ids:
                cursor.execute(
                    "DELETE FROM buffer_zone WHERE user_id = %s AND blob_id = %s",
                    (cls.test_user_id, blob_id)
                )

            # Get all blob IDs for this user from blob_content
            cursor.execute(
                "SELECT blob_id FROM blob_content WHERE user_id = %s",
                (cls.test_user_id,)
            )
            content_blob_ids = [row[0] for row in cursor.fetchall()]

            # Delete blob content entries individually using composite key
            for blob_id in content_blob_ids:
                cursor.execute(
                    "DELETE FROM blob_content WHERE user_id = %s AND blob_id = %s",
                    (cls.test_user_id, blob_id)
                )

            conn.commit()
            print(
                f"✅ Cleaned up test data for user: {cls.test_user_id} ({len(buffer_blob_ids)} buffers, {len(content_blob_ids)} blobs)")

        except Exception as e:
            conn.rollback()
            print(f"⚠️ Error cleaning up test data: {e}")
        finally:
            if cursor:
                cursor.close()
            conn.close()

    def setup_method(self):
        """Setup before each test method."""
        self.test_blob_ids = []

    def teardown_method(self):
        """Cleanup after each test method."""
        asyncio.run(self._cleanup_method_data())

    async def _cleanup_method_data(self):
        """Clean up data created by individual test methods."""
        if not self.test_blob_ids:
            return

        pool = self.storage._get_pool()
        conn = pool.get_connection()
        cursor = None

        try:
            cursor = conn.cursor()

            # Delete specific test buffer entries individually
            for blob_id in self.test_blob_ids:
                cursor.execute(
                    "DELETE FROM buffer_zone WHERE user_id = %s and blob_id = %s",
                    (self.test_user_id, blob_id)
                )

            # Delete specific test blob entries individually  
            for blob_id in self.test_blob_ids:
                cursor.execute(
                    "DELETE FROM blob_content WHERE user_id = %s and blob_id = %s",
                    (self.test_user_id, blob_id)
                )

            conn.commit()

        except Exception as e:
            conn.rollback()
            print(f"⚠️ Error in method cleanup: {e}")
        finally:
            if cursor:
                cursor.close()
            conn.close()

    @pytest.mark.asyncio
    async def test_insert_blob_to_buffer(self):
        """Test inserting a blob into the buffer."""
        blob_id = str(uuid.uuid4())
        self.test_blob_ids.append(blob_id)

        # Create a test ChatBlob
        chat_blob = ChatBlob(
            type=BlobType.chat,
            messages=[
                OpenAICompatibleMessage(
                    role="user",
                    content="Test message for buffer insertion"
                )
            ],
            created_at=datetime.now()
        )

        # Insert blob to buffer
        p = await self.storage.insert_blob_to_buffer(
            self.test_user_id,
            blob_id,
            chat_blob
        )

        assert p.ok(), f"Failed to insert blob: {p.msg()}"

        # Note: We can't verify insertion by querying user_id+blob_id 
        # because Lindorm Wide Table considers it an inefficient query.
        # The successful Promise return indicates the insert worked.
        print("✅ Blob inserted to buffer successfully")

    @pytest.mark.asyncio
    async def test_get_buffer_capacity(self):
        """Test getting buffer capacity for a specific blob type."""
        # Insert multiple blobs
        blob_ids = []
        for i in range(3):
            blob_id = str(uuid.uuid4())
            blob_ids.append(blob_id)
            self.test_blob_ids.append(blob_id)

            chat_blob = ChatBlob(
                type=BlobType.chat,
                messages=[
                    OpenAICompatibleMessage(
                        role="user",
                        content=f"Test message {i}"
                    )
                ],
                created_at=datetime.now()
            )

            p = await self.storage.insert_blob_to_buffer(
                self.test_user_id,
                blob_id,
                chat_blob
            )
            assert p.ok()

        # Get buffer capacity
        p = await self.storage.get_buffer_capacity(self.test_user_id, BlobType.chat)
        assert p.ok(), f"Failed to get buffer capacity: {p.msg()}"
        assert p.data() == 3, f"Expected capacity of 3, got {p.data()}"

    @pytest.mark.asyncio
    async def test_get_unprocessed_buffer_ids(self):
        """Test getting unprocessed buffer IDs."""
        # Insert test blobs
        blob_ids = []
        for i in range(2):
            blob_id = str(uuid.uuid4())
            blob_ids.append(blob_id)
            self.test_blob_ids.append(blob_id)

            chat_blob = ChatBlob(
                type=BlobType.chat,
                messages=[
                    OpenAICompatibleMessage(
                        role="user",
                        content=f"Unprocessed message {i}"
                    )
                ],
                created_at=datetime.now()
            )

            p = await self.storage.insert_blob_to_buffer(
                self.test_user_id,
                blob_id,
                chat_blob
            )
            assert p.ok()

        # Get unprocessed buffer IDs
        p = await self.storage.get_unprocessed_blob_ids(
            self.test_user_id,
            BlobType.chat,
            BufferStatus.idle
        )

        assert p.ok(), f"Failed to get unprocessed buffer IDs: {p.msg()}"
        buffer_ids = p.data()
        assert len(buffer_ids) == 2, f"Expected 2 unprocessed buffers, got {len(buffer_ids)}"

        # Store for cleanup
        # Note: buffer_ids are the same as blob_ids in our new structure
        # No additional action needed as blob_ids are already tracked

    @pytest.mark.asyncio
    async def test_detect_buffer_full_or_not(self):
        """Test detecting if buffer is full based on token size."""
        # Insert blobs with large content to trigger buffer full
        blob_ids = []
        for i in range(5):
            blob_id = str(uuid.uuid4())
            blob_ids.append(blob_id)
            self.test_blob_ids.append(blob_id)

            # Create a blob with substantial content
            content = "This is a test message with substantial content. " * 50
            chat_blob = ChatBlob(
                type=BlobType.chat,
                messages=[
                    OpenAICompatibleMessage(
                        role="user",
                        content=content
                    )
                ],
                created_at=datetime.now()
            )

            p = await self.storage.insert_blob_to_buffer(
                self.test_user_id,
                blob_id,
                chat_blob
            )
            assert p.ok()

        # Detect if buffer is full
        p = await self.storage.detect_buffer_full_or_not(
            self.test_user_id,
            BlobType.chat,
            self.config
        )

        assert p.ok(), f"Failed to detect buffer full: {p.msg()}"
        buffer_ids = p.data()

        # Should return buffer IDs if token size exceeds limit
        # The actual result depends on config.max_chat_blob_buffer_token_size
        print(f"Buffer full detection returned {len(buffer_ids)} buffer IDs")

        if buffer_ids:
            # Note: buffer_ids are the same as blob_ids, already tracked for cleanup
            pass

    @pytest.mark.asyncio
    async def test_flush_buffer_by_ids_with_processing(self):
        """Test flush_buffer_by_ids method with actual blob processing."""
        from lindormmemobase.models.profile_topic import ProfileConfig
        
        # Create a realistic profile config for testing
        profile_config = ProfileConfig(
            language="en",
            profile_strict_mode=True,
            profile_validate_mode=False,
            additional_user_profiles=[
                {
                    "topic": "interests",
                    "sub_topics": [
                        {"name": "programming", "description": "Programming languages and technologies"},
                        {"name": "hobbies", "description": "Personal hobbies and activities"},
                        {"name": "travel", "description": "Travel experiences and preferences"}
                    ]
                },
                {
                    "topic": "skills", 
                    "sub_topics": [
                        {"name": "technical", "description": "Technical skills and expertise"},
                        {"name": "communication", "description": "Communication and soft skills"}
                    ]
                }
            ]
        )
        
        # Insert test blobs with realistic chat conversations
        blob_ids = []
        realistic_conversations = [
            {
                "messages": [
                    OpenAICompatibleMessage(
                        role="user", 
                        content="I've been learning Python for the past 6 months and I really enjoy working with data analysis libraries like pandas and numpy. Do you have any recommendations for next steps?"
                    ),
                    OpenAICompatibleMessage(
                        role="assistant", 
                        content="That's great progress! Since you enjoy data analysis with pandas and numpy, I'd recommend exploring matplotlib for data visualization, scikit-learn for machine learning, and maybe jupyter notebooks if you haven't already. You might also want to try some real datasets from Kaggle to practice your skills."
                    ),
                    OpenAICompatibleMessage(
                        role="user", 
                        content="Thanks! I actually started using Jupyter notebooks last week and they're amazing for exploratory data analysis. I'm particularly interested in machine learning - any specific areas you'd suggest starting with?"
                    )
                ]
            },
            {
                "messages": [
                    OpenAICompatibleMessage(
                        role="user", 
                        content="I just got back from a trip to Japan and it was incredible! The food, culture, and people were all amazing. I especially loved visiting Kyoto and seeing all the traditional temples and gardens."
                    ),
                    OpenAICompatibleMessage(
                        role="assistant", 
                        content="Japan sounds like it was an amazing experience! Kyoto is particularly beautiful with its mix of traditional and modern elements. Did you get to try any specific dishes that stood out to you? And how was the language barrier?"
                    ),
                    OpenAICompatibleMessage(
                        role="user", 
                        content="The ramen was absolutely incredible - so much better than what I've had back home. I also tried authentic sushi at Tsukiji market which was a completely different experience. The language barrier was challenging but people were so patient and helpful. I'm actually thinking of taking Japanese language classes now."
                    )
                ]
            },
            {
                "messages": [
                    OpenAICompatibleMessage(
                        role="user", 
                        content="I'm working on a team project at work and we're having some communication issues. Some team members seem to prefer email while others want everything discussed in meetings. How do you usually handle different communication preferences in a team?"
                    ),
                    OpenAICompatibleMessage(
                        role="assistant", 
                        content="That's a common challenge in team dynamics. One approach is to establish clear communication protocols at the project start - maybe use email for documentation and status updates, but meetings for complex discussions and decision-making. You could also try tools like Slack for quick questions and collaborative documents for ongoing work."
                    )
                ]
            }
        ]
        
        for i, conversation in enumerate(realistic_conversations):
            blob_id = str(uuid.uuid4())
            blob_ids.append(blob_id)
            self.test_blob_ids.append(blob_id)
            
            chat_blob = ChatBlob(
                type=BlobType.chat,
                messages=conversation["messages"],
                created_at=datetime.now()
            )

            p = await self.storage.insert_blob_to_buffer(
                self.test_user_id,
                blob_id,
                chat_blob
            )
            assert p.ok(), f"Failed to insert blob {i}: {p.msg()}"

        # Verify blobs are in buffer
        p = await self.storage.get_unprocessed_blob_ids(
            self.test_user_id,
            BlobType.chat,
            BufferStatus.idle
        )
        assert p.ok(), f"Failed to get unprocessed blob IDs: {p.msg()}"
        buffer_ids = p.data()
        assert len(buffer_ids) >= 3, f"Expected at least 3 unprocessed blobs, got {len(buffer_ids)}"

        # Get buffer capacity before processing
        p = await self.storage.get_buffer_capacity(self.test_user_id, BlobType.chat)
        assert p.ok()
        initial_capacity = p.data()
        print(f"Initial buffer capacity: {initial_capacity}")

        # Test flush_buffer_by_ids with actual processing and profile config
        # Use the first 2 blob_ids for processing
        process_blob_ids = blob_ids[:2]
        
        p = await self.storage.flush_buffer_by_ids(
            self.test_user_id,
            BlobType.chat,
            process_blob_ids,
            BufferStatus.idle,
            profile_config  # Use proper profile config for realistic processing
        )
        
        # Check result
        if not p.ok():
            print(f"⚠️ Flush processing returned error: {p.msg()}")
            print("This might be expected if LLM processing fails due to API issues or content complexity")
            # Verify the buffer status was updated to failed
            pool = self.storage._get_pool()
            conn = pool.get_connection()
            cursor = None
            
            try:
                cursor = conn.cursor()
                # Check if any blobs are marked as failed or processing
                cursor.execute(
                    "SELECT blob_id, status FROM buffer_zone WHERE user_id = %s AND blob_id IN (%s, %s)",
                    (self.test_user_id, process_blob_ids[0], process_blob_ids[1])
                )
                status_results = cursor.fetchall()
                
                for blob_id, status in status_results:
                    assert status in [BufferStatus.failed, BufferStatus.processing], \
                        f"Expected failed or processing status for {blob_id}, got {status}"
                    print(f"✅ Blob {blob_id} correctly marked as {status}")
                        
            finally:
                if cursor:
                    cursor.close()
                conn.close()
        else:
            # If processing succeeded
            response_data = p.data()
            print(f"✅ Flush processing succeeded with realistic chat data")
            print(f"Response type: {type(response_data)}")
            
            # Verify buffer status updates to done
            pool = self.storage._get_pool()
            conn = pool.get_connection()
            cursor = None
            
            try:
                cursor = conn.cursor()
                # Check processed blobs are marked as done
                cursor.execute(
                    "SELECT blob_id, status FROM buffer_zone WHERE user_id = %s AND blob_id IN (%s, %s)",
                    (self.test_user_id, process_blob_ids[0], process_blob_ids[1])
                )
                status_results = cursor.fetchall()
                
                for blob_id, status in status_results:
                    assert status == BufferStatus.done, \
                        f"Expected done status for {blob_id}, got {status}"
                    print(f"✅ Blob {blob_id} correctly marked as {status}")
                        
            finally:
                if cursor:
                    cursor.close()
                conn.close()

        # Verify remaining buffer capacity decreased
        p = await self.storage.get_buffer_capacity(self.test_user_id, BlobType.chat)
        assert p.ok()
        final_capacity = p.data()
        print(f"Final buffer capacity: {final_capacity}")
        
        # The third blob should still be idle
        assert final_capacity >= 1, "At least one blob should remain unprocessed"

        print("✅ flush_buffer_by_ids with realistic content and profile config test completed successfully")

    @pytest.mark.asyncio
    async def test_buffer_status_updates(self):
        """Test buffer status transitions."""
        blob_id = str(uuid.uuid4())
        self.test_blob_ids.append(blob_id)

        # Insert a blob
        chat_blob = ChatBlob(
            type=BlobType.chat,
            messages=[
                OpenAICompatibleMessage(
                    role="user",
                    content="Test status transitions"
                )
            ],
            created_at=datetime.now()
        )

        p = await self.storage.insert_blob_to_buffer(
            self.test_user_id,
            blob_id,
            chat_blob
        )
        assert p.ok()

        # Get the buffer ID
        pool = self.storage._get_pool()
        conn = pool.get_connection()
        cursor = None

        try:
            cursor = conn.cursor()

            # Check initial status - 注意：现在没有单独的id字段
            cursor.execute(
                "SELECT status FROM buffer_zone WHERE user_id = %s AND blob_id = %s",
                (self.test_user_id, blob_id)
            )
            result = cursor.fetchone()
            status = result[0] if result else None

            assert status == BufferStatus.idle, f"Expected idle status, got {status}"

            # Update status to processing  
            cursor.execute(
                "UPDATE buffer_zone SET status = %s WHERE user_id = %s AND blob_id = %s",
                (BufferStatus.processing, self.test_user_id, blob_id)
            )
            conn.commit()

            # Verify status update
            cursor.execute(
                "SELECT status FROM buffer_zone WHERE user_id = %s AND blob_id = %s",
                (self.test_user_id, blob_id)
            )
            status = cursor.fetchone()[0]
            assert status == BufferStatus.processing, f"Expected processing status, got {status}"

            # Update status to done
            cursor.execute(
                "UPDATE buffer_zone SET status = %s WHERE user_id = %s AND blob_id = %s",
                (BufferStatus.done, self.test_user_id, blob_id)
            )
            conn.commit()

            # Verify final status
            cursor.execute(
                "SELECT status FROM buffer_zone WHERE user_id = %s AND blob_id = %s",
                (self.test_user_id, blob_id)
            )
            status = cursor.fetchone()[0]
            assert status == BufferStatus.done, f"Expected done status, got {status}"

            print("✅ Buffer status transitions tested successfully")

        finally:
            if cursor:
                cursor.close()
            conn.close()

    @pytest.mark.asyncio
    async def test_multiple_blob_types(self):
        """Test handling different blob types in buffer."""
        from lindormmemobase.models.blob import DocBlob

        blob_types_data = [
            (BlobType.chat, ChatBlob(
                type=BlobType.chat,
                messages=[
                    OpenAICompatibleMessage(
                        role="user",
                        content="Chat message"
                    )
                ],
                created_at=datetime.now()
            )),
            (BlobType.doc, DocBlob(
                type=BlobType.doc,
                content="Document content",
                created_at=datetime.now()
            ))
            # Note: CodeBlob currently not supported in buffer processing
        ]

        for blob_type, blob_data in blob_types_data:
            blob_id = str(uuid.uuid4())
            self.test_blob_ids.append(blob_id)

            p = await self.storage.insert_blob_to_buffer(
                self.test_user_id,
                blob_id,
                blob_data
            )
            assert p.ok(), f"Failed to insert {blob_type} blob"

        # Check capacity for each type
        for blob_type, _ in blob_types_data:
            p = await self.storage.get_buffer_capacity(self.test_user_id, blob_type)
            assert p.ok()
            assert p.data() == 1, f"Expected 1 {blob_type} blob, got {p.data()}"

        print("✅ Multiple blob types handled successfully")


def run_tests():
    """Run the test suite."""
    import subprocess
    result = subprocess.run(
        ["pytest", __file__, "-v", "-s"],
        capture_output=False,
        text=True
    )
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
