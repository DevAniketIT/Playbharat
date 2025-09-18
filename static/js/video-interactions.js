// PlayBharat Video Interactions - Like, Dislike, Comments
document.addEventListener('DOMContentLoaded', function() {
    
    // Use PlayBharat utils for CSRF token
    const getCsrfToken = () => window.PlayBharat?.utils?.getCsrfToken() || '';
    
    // Like/Dislike functionality
    const likeBtn = document.getElementById('like-btn');
    const dislikeBtn = document.getElementById('dislike-btn');
    
    if (likeBtn) {
        likeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleVideoReaction('like');
        });
    }
    
    if (dislikeBtn) {
        dislikeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleVideoReaction('dislike');
        });
    }
    
    function handleVideoReaction(type) {
        const videoId = document.querySelector('[data-video-id]')?.dataset.videoId;
        
        if (!videoId) {
            console.error('Video ID not found');
            return;
        }
        
        // Check if user is logged in
        if (!document.body.dataset.userAuthenticated) {
            showLoginPrompt();
            return;
        }
        
        // Show loading state
        const btn = type === 'like' ? likeBtn : dislikeBtn;
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Loading...';
        btn.disabled = true;
        
        fetch(`/interactions/video/${videoId}/like/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `type=${type}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateReactionButtons(data);
                showToast(`${type === 'like' ? 'Liked' : 'Disliked'}!`, 'success');
            } else {
                showToast('Error: ' + (data.error || 'Failed to react'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error occurred', 'error');
        })
        .finally(() => {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        });
    }
    
    function updateReactionButtons(data) {
        // Update like button
        const likeCount = document.getElementById('like-count');
        const dislikeCount = document.getElementById('dislike-count');
        
        if (likeCount) likeCount.textContent = data.like_count;
        if (dislikeCount) dislikeCount.textContent = data.dislike_count;
        
        // Update button states
        likeBtn?.classList.toggle('active', data.reacted && data.reaction_type === 'like');
        dislikeBtn?.classList.toggle('active', data.reacted && data.reaction_type === 'dislike');
    }
    
    // Comment System
    const commentForm = document.getElementById('comment-form');
    const commentsList = document.getElementById('comments-list');
    
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitComment();
        });
    }
    
    function submitComment() {
        const formData = new FormData(commentForm);
        const submitBtn = commentForm.querySelector('button[type="submit"]');
        const textarea = commentForm.querySelector('textarea');
        
        // Check if user is logged in
        if (!document.body.dataset.userAuthenticated) {
            showLoginPrompt();
            return;
        }
        
        // Validate comment content
        const content = textarea.value.trim();
        if (!content) {
            showToast('Please enter a comment', 'warning');
            return;
        }
        
        // Show loading state
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Posting...';
        submitBtn.disabled = true;
        
        fetch('/interactions/comment/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                addCommentToDOM(data.comment);
                textarea.value = '';
                updateCommentCount(1);
                showToast('Comment posted!', 'success');
            } else {
                showToast('Error: ' + (data.error || 'Failed to post comment'), 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error occurred', 'error');
        })
        .finally(() => {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        });
    }
    
    function addCommentToDOM(comment) {
        const commentElement = document.createElement('div');
        commentElement.className = 'comment-item mb-3 p-3 border rounded';
        commentElement.id = `comment-${comment.id}`;
        
        commentElement.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="comment-avatar me-3">
                    <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <span class="text-white fw-bold">${comment.author.charAt(0).toUpperCase()}</span>
                    </div>
                </div>
                <div class="comment-content flex-grow-1">
                    <div class="comment-header mb-2">
                        <strong class="comment-author">${comment.author}</strong>
                        <small class="text-muted ms-2">${formatDate(comment.created_at)}</small>
                    </div>
                    <div class="comment-text">${comment.content}</div>
                    <div class="comment-actions mt-2">
                        <button class="btn btn-sm btn-outline-primary comment-like-btn" data-comment-id="${comment.id}">
                            <i class="bi bi-hand-thumbs-up me-1"></i>0
                        </button>
                        <button class="btn btn-sm btn-outline-secondary ms-2 comment-reply-btn" data-comment-id="${comment.id}">
                            <i class="bi bi-reply me-1"></i>Reply
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        commentsList?.insertBefore(commentElement, commentsList.firstChild);
    }
    
    // Comment like functionality
    document.addEventListener('click', function(e) {
        if (e.target.closest('.comment-like-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.comment-like-btn');
            const commentId = btn.dataset.commentId;
            handleCommentLike(commentId, btn);
        }
        
        if (e.target.closest('.comment-reply-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.comment-reply-btn');
            const commentId = btn.dataset.commentId;
            showReplyForm(commentId);
        }
    });
    
    function handleCommentLike(commentId, btn) {
        if (!document.body.dataset.userAuthenticated) {
            showLoginPrompt();
            return;
        }
        
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        btn.disabled = true;
        
        fetch(`/interactions/comment/${commentId}/like/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                btn.innerHTML = `<i class="bi bi-hand-thumbs-up me-1"></i>${data.like_count}`;
                btn.classList.toggle('btn-outline-primary', !data.liked);
                btn.classList.toggle('btn-primary', data.liked);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            btn.innerHTML = originalHTML;
        })
        .finally(() => {
            btn.disabled = false;
        });
    }
    
    function showReplyForm(commentId) {
        // Remove any existing reply forms
        const existingForms = document.querySelectorAll('.reply-form');
        existingForms.forEach(form => form.remove());
        
        const commentElement = document.getElementById(`comment-${commentId}`);
        if (!commentElement) return;
        
        const replyForm = document.createElement('div');
        replyForm.className = 'reply-form mt-3 p-3 bg-light rounded';
        replyForm.innerHTML = `
            <form class="reply-form-inner">
                <input type="hidden" name="parent_id" value="${commentId}">
                <div class="mb-3">
                    <textarea class="form-control" name="content" rows="3" placeholder="Write a reply..." required></textarea>
                </div>
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-primary btn-sm">
                        <i class="bi bi-reply me-1"></i>Post Reply
                    </button>
                    <button type="button" class="btn btn-outline-secondary btn-sm cancel-reply">
                        Cancel
                    </button>
                </div>
            </form>
        `;
        
        commentElement.appendChild(replyForm);
        replyForm.querySelector('textarea').focus();
        
        // Handle reply form submission
        replyForm.querySelector('.reply-form-inner').addEventListener('submit', function(e) {
            e.preventDefault();
            submitReply(this, commentId);
        });
        
        // Handle cancel
        replyForm.querySelector('.cancel-reply').addEventListener('click', function() {
            replyForm.remove();
        });
    }
    
    function submitReply(form, parentId) {
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const textarea = form.querySelector('textarea');
        
        submitBtn.textContent = 'Posting...';
        submitBtn.disabled = true;
        
        fetch(`/interactions/comment/${parentId}/reply/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Add reply to DOM (simplified)
                showToast('Reply posted!', 'success');
                form.closest('.reply-form').remove();
                // You might want to reload comments or add the reply dynamically
                location.reload(); // Simple solution for now
            } else {
                showToast('Error posting reply', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Network error occurred', 'error');
        })
        .finally(() => {
            submitBtn.textContent = 'Post Reply';
            submitBtn.disabled = false;
        });
    }
    
    // Subscribe functionality
    const subscribeBtn = document.getElementById('subscribe-btn');
    if (subscribeBtn) {
        subscribeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleSubscribe();
        });
    }
    
    function handleSubscribe() {
        const channelId = subscribeBtn.dataset.channelId;
        
        if (!document.body.dataset.userAuthenticated) {
            showLoginPrompt();
            return;
        }
        
        const originalHTML = subscribeBtn.innerHTML;
        subscribeBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Loading...';
        subscribeBtn.disabled = true;
        
        fetch('/interactions/subscribe/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `channel_id=${channelId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.subscribed) {
                    subscribeBtn.innerHTML = '<i class="bi bi-check-circle me-2"></i>Subscribed';
                    subscribeBtn.className = 'btn btn-outline-primary flex-grow-1';
                } else {
                    subscribeBtn.innerHTML = '<i class="bi bi-plus-circle me-2"></i>Subscribe';
                    subscribeBtn.className = 'btn btn-primary flex-grow-1';
                }
                
                // Update subscriber count
                const subCount = document.getElementById('subscriber-count');
                if (subCount) {
                    subCount.textContent = `${data.subscriber_count} subscribers`;
                }
                
                showToast(data.subscribed ? 'Subscribed!' : 'Unsubscribed!', 'success');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            subscribeBtn.innerHTML = originalHTML;
        })
        .finally(() => {
            subscribeBtn.disabled = false;
        });
    }
    
    // Utility functions
    function showLoginPrompt() {
        if (confirm('You need to be logged in to perform this action. Would you like to log in?')) {
            window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
        }
    }
    
    // Use PlayBharat utils for toast notifications
    const showToast = (message, type = 'info') => {
        if (window.PlayBharat?.utils?.showToast) {
            window.PlayBharat.utils.showToast(message, type);
        } else {
            // Fallback for when PlayBharat is not loaded
            console.log(`Toast: ${message} (${type})`);
        }
    };
    
    function updateCommentCount(delta) {
        const commentCountElement = document.getElementById('comment-count');
        if (commentCountElement) {
            const current = parseInt(commentCountElement.textContent) || 0;
            commentCountElement.textContent = current + delta;
        }
    }
    
    // Use PlayBharat utils for date formatting
    const formatDate = (dateString) => {
        if (window.PlayBharat?.utils?.formatTimeAgo) {
            return window.PlayBharat.utils.formatTimeAgo(dateString);
        } else {
            // Simple fallback
            return new Date(dateString).toLocaleDateString();
        }
    };
    
    // Share functionality
    const shareBtn = document.getElementById('share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function(e) {
            e.preventDefault();
            showShareModal();
        });
    }
    
    function showShareModal() {
        const videoId = document.querySelector('[data-video-id]')?.dataset.videoId;
        const videoTitle = document.querySelector('h1')?.textContent || 'Video';
        const currentUrl = window.location.href;
        
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Share Video</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label">Video URL:</label>
                            <div class="input-group">
                                <input type="text" class="form-control" value="${currentUrl}" readonly id="share-url">
                                <button class="btn btn-outline-secondary" type="button" onclick="copyToClipboard()">Copy</button>
                            </div>
                        </div>
                        <div class="d-grid gap-2">
                            <button class="btn btn-success" onclick="shareOn('whatsapp')">
                                <i class="bi bi-whatsapp me-2"></i>WhatsApp
                            </button>
                            <button class="btn btn-primary" onclick="shareOn('facebook')">
                                <i class="bi bi-facebook me-2"></i>Facebook
                            </button>
                            <button class="btn btn-info" onclick="shareOn('twitter')">
                                <i class="bi bi-twitter me-2"></i>Twitter
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        new bootstrap.Modal(modal).show();
        
        // Clean up modal after hide
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    // Global functions for share modal
    window.copyToClipboard = function() {
        const urlInput = document.getElementById('share-url');
        urlInput.select();
        document.execCommand('copy');
        showToast('URL copied to clipboard!', 'success');
        
        // Track share
        const videoId = document.querySelector('[data-video-id]')?.dataset.videoId;
        if (videoId) {
            fetch(`/interactions/video/${videoId}/share/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCsrfToken()
                },
                body: 'platform=copy_link'
            });
        }
    };
    
    window.shareOn = function(platform) {
        const url = encodeURIComponent(window.location.href);
        const title = encodeURIComponent(document.querySelector('h1')?.textContent || 'Check out this video');
        
        let shareUrl = '';
        switch (platform) {
            case 'whatsapp':
                shareUrl = `https://wa.me/?text=${title} ${url}`;
                break;
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                break;
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?text=${title}&url=${url}`;
                break;
        }
        
        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
            
            // Track share
            const videoId = document.querySelector('[data-video-id]')?.dataset.videoId;
            if (videoId) {
                fetch(`/interactions/video/${videoId}/share/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: `platform=${platform}`
                });
            }
        }
    };
});