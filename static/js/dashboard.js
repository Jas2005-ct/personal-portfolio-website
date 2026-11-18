$(document).ready(function() {
            // Navigation
            $('.nav-link').click(function(e) {
                if ($(this).data('target')) {
                    e.preventDefault();
                    $('.nav-link').removeClass('active');
                    $(this).addClass('active');
                    $('.section').hide();
                    $('#' + $(this).data('target') + '-section').fadeIn();
                }
                // Close sidebar on mobile after selecting a section
                if (window.innerWidth <= 900) {
                    $('.sidebar').removeClass('open');
                }
            });

            // Mobile sidebar toggle
            $('#sidebarToggle').click(function() {
                $('.sidebar').toggleClass('open');
            });

            // Helper: Get CSRF Token
            function getCookie(name) {
                let cookieValue = null;
                if (document.cookie && document.cookie !== '') {
                    const cookies = document.cookie.split(';');
                    for (let i = 0; i < cookies.length; i++) {
                        const cookie = cookies[i].trim();
                        if (cookie.substring(0, name.length + 1) === (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            const csrftoken = getCookie('csrftoken');

            $.ajaxSetup({
                headers: { 'X-CSRFToken': csrftoken }
            });

            // Shared state for the tech stack after profile loads
            let currentProfileTechs = [];

            // Fetch Initial Data (decoupled — each loads independently)
            loadData();

            function loadData() {
                loadProfile();
                loadSections();
                // Social
                $.get('/api/social-links/', function(data) {
                    if (data.length > 0) {
                        const social = data[0];
                        $('#social-id').val(social.id);
                        $('input[name="github"]').val(social.github);
                        $('input[name="linkedin"]').val(social.linkedin);
                        $('input[name="twitter"]').val(social.twitter);
                        $('input[name="instagram"]').val(social.instagram);
                        $('input[name="facebook"]').val(social.facebook);
                    }
                });
                // Resume
                $.get('/api/resume/', function(data) {
                    if (data.length > 0) {
                        const resume = data[0];
                        $('#resume-id').val(resume.id);
                        $('#current-resume-link').attr('href', resume.file_url).show();
                    }
                });
                // Lists
                loadList('education', '#education-list');
                loadList('professions', '#professions-list');
                loadList('certificates', '#certificates-list');
                loadList('projects', '#projects-list');
            }

            function loadProfile() {
                $.ajax({
                    url: '/api/profile/',
                    type: 'GET',
                    dataType: 'json',
                    success: function(data) {
                        if (data.length > 0) {
                            const profile = data[0];
                            $('#profile-id').val(profile.id);
                            $('input[name="name"]').val(profile.name);
                            $('input[name="title"]').val(profile.title);
                            $('textarea[name="bio"]').val(profile.bio);
                            $('textarea[name="philosophy"]').val(profile.philosophy);
                            $('input[name="phone"]').val(profile.phone);
                            $('textarea[name="address"]').val(profile.address);
                            $('#profile-tech-id').val(profile.id);
                            currentProfileTechs = profile.technologies || [];
                            // Sync Tom Select selection if already initialized
                            if (profileTechSelect) {
                                profileTechSelect.setValue(currentProfileTechs.map(t => t.id.toString()));
                            }
                            renderSelectedTechs(currentProfileTechs);
                        }
                    },
                    error: function(err) {
                        console.error('Error loading profile:', err);
                    }
                });
            }

            // Handle Create Section
            $('#create-section-form').submit(function(e) {
                e.preventDefault();
                let name = $(this).find('input[name="name"]').val();
                $.ajax({
                    url: '/api/tech-sections/',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({ name: name }),
                    success: function() {
                        Swal.fire({ icon: 'success', title: 'Created!', text: 'Section created.', timer: 1500, showConfirmButton: false });
                        $('#create-section-form')[0].reset();
                        loadSections();
                    },
                    error: function(err) {
                        console.error(err);
                        Swal.fire({ icon: 'error', title: 'Error', text: 'Failed to create section.' });
                    }
                });
            });

            // Handle Add Tech to Section
            $(document).on('submit', '.add-tech-to-section-form', function(e) {
                e.preventDefault();
                let form = $(this);
                let sectionId = form.data('section-id');
                let formData = new FormData(this);
                formData.append('section', sectionId);
                // Remove empty file entry if no file selected
                let iconInput = form.find('input[name="icon"]')[0];
                if (iconInput && iconInput.files.length === 0) {
                    formData.delete('icon');
                }

                $.ajax({
                    url: '/api/tech-stack/',
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function() {
                        Swal.fire({ icon: 'success', title: 'Added!', text: 'Technology added.', timer: 1500, showConfirmButton: false });
                        loadSections();
                    },
                    error: function(err) {
                        console.error(err);
                        let msg = 'Failed to add technology.';
                        if (err.responseJSON && err.responseJSON.error) {
                            msg = err.responseJSON.error;
                        }
                        Swal.fire({ icon: 'error', title: 'Error', text: msg });
                    }
                });
            });

            // Handle Delete Tech
            $(document).on('click', '.delete-tech-btn', function() {
                let id = $(this).data('id');
                Swal.fire({
                    title: 'Delete this technology?', text: "You won't be able to revert this!", icon: 'warning',
                    showCancelButton: true, confirmButtonColor: '#d33', confirmButtonText: 'Yes, delete it!'
                }).then(result => {
                    if (result.isConfirmed) {
                        $.ajax({
                            url: `/api/tech-stack/${id}/`,
                            type: 'DELETE',
                            success: function() {
                                loadSections();
                                Swal.fire({ icon: 'success', title: 'Deleted!', timer: 1500, showConfirmButton: false });
                            }
                        });
                    }
                });
            });

            // Handle Delete Section
            $(document).on('click', '.delete-section-btn', function() {
                let id = $(this).data('id');
                Swal.fire({
                    title: 'Delete this section?', text: 'All technologies in this section will also be deleted.', icon: 'warning',
                    showCancelButton: true, confirmButtonColor: '#d33', confirmButtonText: 'Yes, delete it!'
                }).then(result => {
                    if (result.isConfirmed) {
                        $.ajax({
                            url: `/api/tech-sections/${id}/`,
                            type: 'DELETE',
                            success: function() {
                                loadSections();
                                Swal.fire({ icon: 'success', title: 'Deleted!', timer: 1500, showConfirmButton: false });
                            }
                        });
                    }
                });
            });

            function loadSections() {
                $.ajax({
                    url: '/api/tech-sections/',
                    type: 'GET',
                    dataType: 'json',
                    success: function(sections) {
                        let sectionOptions = '<option value="">Select Section</option>';
                        if (sections && sections.length > 0) {
                            sections.forEach(section => {
                                sectionOptions += `<option value="${section.id}">${section.name}</option>`;
                            });
                        }
                        $('#tag-section-select').html(sectionOptions);
                        renderTechStackBySection(sections || []);
                    },
                    error: function(err) {
                        console.error('Error loading sections:', err);
                        $('#tech-stack-by-section').html('<div class="card p-4 mb-4 text-danger"><p class="mb-0">Failed to load sections. Please refresh the page.</p></div>');
                        updateTechSelectOptions([]);
                    }
                });
            }

            function renderTechStackBySection(sections) {
                if (!sections || sections.length === 0) {
                    $('#tech-stack-by-section').html('<div class="card p-4 mb-4"><p class="text-muted mb-0">No sections created yet. Create one above.</p></div>');
                    updateTechSelectOptions([]);
                    return;
                }

                $.ajax({
                    url: '/api/tech-stack/',
                    type: 'GET',
                    dataType: 'json',
                    success: function(techs) {
                        let html = '';
                        sections.forEach(section => {
                            const sectionTechs = (techs || []).filter(t => t.section === section.id);
                            const techBadges = sectionTechs.length > 0
                                ? sectionTechs.map(t => `
                                    <span class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-slate_blue/10 text-slate_blue mr-2 mb-2 border border-slate_blue/30">
                                        ${t.icon ? `<img src="${t.icon}" alt="" class="w-4 h-4 object-contain mr-1">` : ''}
                                        ${t.name}
                                        <button class="delete-tech-btn hover:text-red-400 ml-1.5 transition-colors focus:outline-none" data-id="${t.id}" aria-label="Remove">
                                            <i class="fas fa-times text-[10px]"></i>
                                        </button>
                                    </span>
                                `).join('')
                                : '<p class="text-muted small mb-0">No technologies in this section yet.</p>';

                            html += `
                                <div class="card p-4 mb-4" data-section-id="${section.id}">
                                    <div class="flex justify-between items-center mb-3">
                                        <h5 class="mb-0">${section.name}</h5>
                                        <button class="btn btn-danger btn-sm delete-section-btn" data-id="${section.id}">
                                            <i class="fas fa-trash"></i> Delete
                                        </button>
                                    </div>
                                    <div class="mb-3">${techBadges}</div>
                                    <form class="add-tech-to-section-form grid grid-cols-12 gap-4" data-section-id="${section.id}">
                                        <div class="md:col-span-6 col-span-12">
                                            <input type="text" class="form-control" name="name" placeholder="Technology name" required>
                                        </div>
                                        <div class="md:col-span-4 col-span-12">
                                            <input type="file" class="form-control" name="icon" accept="image/*">
                                        </div>
                                        <div class="md:col-span-2 col-span-12">
                                            <button type="submit" class="btn btn-primary w-full">Add</button>
                                        </div>
                                    </form>
                                </div>
                            `;
                        });
                        $('#tech-stack-by-section').html(html || '<div class="card p-4 mb-4"><p class="text-muted mb-0">No sections created yet. Create one above.</p></div>');
                        updateTechSelectOptions(techs || []);
                    },
                    error: function(err) {
                        console.error('Error loading tech stack:', err);
                        $('#tech-stack-by-section').html('<div class="card p-4 mb-4 text-danger"><p class="mb-0">Failed to load technologies. Please refresh the page.</p></div>');
                        updateTechSelectOptions([]);
                    }
                });
            }


            let profileTechSelect = null;
            let projectTechSelect = null;

            function updateTechSelectOptions(techs) {
                // Build unique section groups from techs
                const groups = {};
                techs.forEach(t => {
                    const gid = t.section.toString();
                    if (!groups[gid]) groups[gid] = { value: gid, label: t.section_name || 'Uncategorized' };
                });
                const groupList = Object.values(groups);

                const opts = techs.map(t => ({value: t.id.toString(), text: t.name, optgroup: t.section.toString()}));
                const selected = currentProfileTechs.map(t => t.id.toString());

                const baseConfig = {
                    placeholder: 'Select Technologies',
                    plugins: ['remove_button'],
                    optgroupField: 'optgroup',
                    optgroups: groupList,
                };

                // Profile Tech Select
                if (!profileTechSelect) {
                    profileTechSelect = new TomSelect('#tech-select', {
                        ...baseConfig,
                        options: opts,
                        items: selected,
                        create: true,
                        createFilter: input => input.trim().length > 0,
                    });
                } else {
                    profileTechSelect.clearOptionGroups();
                    profileTechSelect.clearOptions();
                    groupList.forEach(g => profileTechSelect.addOptionGroup(g.value, g));
                    profileTechSelect.addOptions(opts);
                    profileTechSelect.setValue(selected);
                }

                // Project Tech Select
                const projectOpts = techs.map(t => ({value: t.id.toString(), text: t.name, optgroup: t.section.toString()}));
                if (!projectTechSelect) {
                    projectTechSelect = new TomSelect('.project-tech-select', {
                        ...baseConfig,
                        options: projectOpts,
                        maxOptions: null,
                    });
                } else {
                    projectTechSelect.clearOptionGroups();
                    projectTechSelect.clearOptions();
                    groupList.forEach(g => projectTechSelect.addOptionGroup(g.value, g));
                    projectTechSelect.addOptions(projectOpts);
                }
            }

            function loadList(endpoint, containerId) {
                $.get('/api/' + endpoint + '/', function(data) {
                    let html = '';
                    data.forEach(item => {
                        let title = item.course || item.role || item.title;
                        let subtitle = item.institution || item.company || item.tech_stack || '';
                        
                        // For professions, show experience type
                        if (endpoint === 'professions') {
                            let expType = item.experience === 'professional' ? '💼 Professional' : '🎓 Internship';
                            subtitle = expType + ' | ' + subtitle;
                        }
                        
                        if (item.location) subtitle += ` | ${item.location}`;
                        
                        html += `
                            <div class="md:col-span-6 col-span-12">
                                <div class="card p-4 h-full">
                                    <div class="flex justify-between items-center h-full">
                                        <div>
                                            <h5 class="mb-1">${title}</h5>
                                            <small class="text-muted">${subtitle}</small>
                                        </div>
                                        <div class="flex items-center gap-2">
                                            <button class="btn btn-warning btn-sm edit-btn" data-endpoint="${endpoint}" data-id="${item.id}">
                                                <i class="fas fa-edit"></i>
                                            </button>
                                            <button class="btn btn-danger btn-sm delete-btn" data-endpoint="${endpoint}" data-id="${item.id}">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    $(containerId).html(html);
                });
            }

            // Handle Profile, Social & Resume Forms (Single Instance)
            $('#profile-form, #social-form, #resume-form').submit(function(e) {
                e.preventDefault();
                let form = $(this);
                let id = form.find('input[name="id"]').val();
                let formData = new FormData(this);
                
                let url = id ? `/api/${form.attr('id').replace('-form', '')}/${id}/` : `/api/${form.attr('id').replace('-form', '')}/`;
                // Fix for social-links endpoint naming mismatch if needed, but standardizing is better.
                // The endpoint for social is 'social-links', but form id is 'social-form'.
                if (form.attr('id') === 'social-form') url = id ? `/api/social-links/${id}/` : `/api/social-links/`;
                if (form.attr('id') === 'resume-form') url = id ? `/api/resume/${id}/` : `/api/resume/`;
                if (form.attr('id') === 'profile-form') url = id ? `/api/profile/${id}/` : `/api/profile/`;
                let method = id ? 'PATCH' : 'POST';

                $.ajax({
                    url: url,
                    type: method,
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function() {
                        Swal.fire({
                            icon: 'success',
                            title: 'Saved!',
                            text: 'Your changes have been saved successfully.',
                            timer: 2000,
                            showConfirmButton: false
                        });
                        loadData();
                    },
                    error: function(err) {
                        console.error(err);
                        Swal.fire({
                            icon: 'error',
                            title: 'Oops...',
                            text: 'Something went wrong! Check console for details.'
                        });
                    }
                });
            });

            // Handle Tech Stack Form
            $('#tech-stack-form').submit(function(e) {
                e.preventDefault();
                let profileId = $('#profile-tech-id').val();
                if (!profileId) {
                    Swal.fire({ icon: 'error', title: 'Error', text: 'Save your profile first before adding tech stack.' });
                    return;
                }

                let selectedValues = profileTechSelect ? profileTechSelect.getValue() : [];
                let existingIds = [];
                let newTags = [];

                selectedValues.forEach(val => {
                    if (isNaN(val)) {
                        newTags.push(val);
                    } else {
                        existingIds.push(parseInt(val));
                    }
                });

                if (newTags.length > 0) {
                    // Show section selection modal
                    let listHtml = '<p class="text-sm text-slate-600 mb-2">New technologies to create:</p><ul class="list-disc list-inside mb-3">';
                    newTags.forEach(tag => { listHtml += `<li class="text-slate-700">${tag}</li>`; });
                    listHtml += '</ul>';
                    $('#new-tags-list').html(listHtml);
                    $('#confirm-tag-section').data('profileId', profileId);
                    $('#confirm-tag-section').data('existingIds', existingIds);
                    $('#confirm-tag-section').data('newTags', newTags);
                    $('#tagSectionModal').removeClass('opacity-0 pointer-events-none invisible').addClass('is-open').attr('aria-hidden', 'false');
                    document.body.style.overflow = 'hidden';
                } else {
                    updateProfileTechStack(profileId, existingIds);
                }
            });

            // Close tag section modal on backdrop/close button
            $('#tagSectionModal').on('click', '[data-modal-close]', function() {
                $('#tagSectionModal').addClass('opacity-0 pointer-events-none invisible').removeClass('is-open').attr('aria-hidden', 'true');
                if (!document.querySelector('.modal-overlay.is-open')) document.body.style.overflow = '';
            });

            $('#confirm-tag-section').click(function() {
                let sectionId = $('#tag-section-select').val();
                if (!sectionId) {
                    Swal.fire({ icon: 'warning', title: 'Required', text: 'Please select a section.' });
                    return;
                }

                let profileId = $(this).data('profileId');
                let existingIds = $(this).data('existingIds');
                let newTags = $(this).data('newTags');

                let promises = newTags.map(tagName => {
                    return $.ajax({
                        url: '/api/tech-stack/',
                        type: 'POST',
                        contentType: 'application/json',
                        data: JSON.stringify({ name: tagName, section: parseInt(sectionId) })
                    });
                });

                Promise.all(promises)
                    .then(results => {
                        results.forEach(res => existingIds.push(res.id));
                        return updateProfileTechStack(profileId, existingIds);
                    })
                    .then(() => {
                        $('#tagSectionModal').addClass('opacity-0 pointer-events-none invisible').removeClass('is-open').attr('aria-hidden', 'true');
                        if (!document.querySelector('.modal-overlay.is-open')) document.body.style.overflow = '';
                    })
                    .catch(err => {
                        console.error(err);
                        Swal.fire({ icon: 'error', title: 'Error', text: 'Failed to create technology.' });
                        $('#tagSectionModal').addClass('opacity-0 pointer-events-none invisible').removeClass('is-open').attr('aria-hidden', 'true');
                        if (!document.querySelector('.modal-overlay.is-open')) document.body.style.overflow = '';
                    });
            });

            function updateProfileTechStack(profileId, techStackIds) {
                return $.ajax({
                    url: `/api/profile/${profileId}/`,
                    type: 'PATCH',
                    contentType: 'application/json',
                    data: JSON.stringify({ tech_stack_ids: techStackIds })
                }).then(data => {
                    Swal.fire({ icon: 'success', title: 'Saved!', text: 'Tech stack updated successfully.', timer: 1500, showConfirmButton: false });
                    currentProfileTechs = data.technologies || [];
                    renderSelectedTechs(currentProfileTechs);
                    loadSections();
                }).catch(err => {
                    console.error(err);
                    Swal.fire({ icon: 'error', title: 'Error', text: 'Failed to update tech stack.' });
                });
            }

            function renderSelectedTechs(technologies) {
                let html = '';
                if (technologies && technologies.length > 0) {
                    technologies.forEach(tech => {
                        html += `
                            <div class="md:col-span-2 col-span-6">
                                <div class="card p-2 text-center">
                                    <span class="badge" style="background-color: var(--primary-color); color: #000; padding: 0.5rem; width: 100%;">${tech.name}</span>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html = '<p class="text-muted">No technologies selected.</p>';
                }
                $('#selected-tech-list').html(html);
            }

            // Handle Add/Edit Forms (Multiple Instances)
            $('.add-form').submit(function(e) {
                e.preventDefault();
                let form = $(this);
                let endpoint = form.data('endpoint');
                let formData = new FormData(this);
                let id = form.find('input[name="id"]').val();
                
                let url = id ? `/api/${endpoint}/${id}/` : `/api/${endpoint}/`;
                let method = id ? 'PATCH' : 'POST';

                $.ajax({
                    url: url,
                    type: method,
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function() {
                        form[0].reset();
                        form.find('input[name="id"]').val(''); // Clear ID
                        if (projectTechSelect) projectTechSelect.clear(); // Reset Tom Select
                        form.find('.submit-btn').text('Add ' + endpoint.slice(0, -1).charAt(0).toUpperCase() + endpoint.slice(0, -1).slice(1)); // Reset button text
                        form.find('.submit-btn').removeClass('btn-warning').addClass('btn-success');
                        form.closest('.card').find('.cancel-edit-btn').hide(); // Hide cancel button
                        loadList(endpoint, '#' + endpoint + '-list');
                        
                        Swal.fire({
                            icon: 'success',
                            title: 'Success!',
                            text: 'Item saved successfully.',
                            timer: 1500,
                            showConfirmButton: false
                        });
                    },
                    error: function(err) {
                        console.error(err);
                        let msg = 'Error saving item.';
                        if (err.responseJSON) {
                            msg = JSON.stringify(err.responseJSON);
                        }
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: msg
                        });
                    }
                });
            });

            // Handle Edit Click
            $(document).on('click', '.edit-btn', function() {
                let btn = $(this);
                let endpoint = btn.data('endpoint');
                let id = btn.data('id');
                
                // Fetch item details
                $.get(`/api/${endpoint}/${id}/`, function(data) {
                    // Find the form for this endpoint
                    let form = $(`.add-form[data-endpoint="${endpoint}"]`);
                    
                    // Populate fields
                    form.find('input[name="id"]').val(data.id);
                    $.each(data, function(key, value) {
                        let input = form.find(`[name="${key}"]`);
                        if (input.attr('type') !== 'file') {
                            if (key === 'tech_stack_ids' && endpoint === 'projects') {
                                // Handle Tom Select for Projects
                                // Assuming 'technologies' is returned with full objects, map to IDs
                                let selectedIds = data.technologies.map(t => t.id);
                                if (projectTechSelect) projectTechSelect.setValue(selectedIds.map(String));
                            } else {
                                input.val(value);
                            }
                        }
                    });

                    // Change UI to Edit Mode
                    form.find('.submit-btn').text('Update Item').removeClass('btn-success').addClass('btn-warning');
                    form.closest('.card').find('.cancel-edit-btn').show();
                    
                    // Scroll to form
                    $('html, body').animate({
                        scrollTop: form.offset().top - 100
                    }, 500);
                });
            });

            // Handle Cancel Edit
            $('.cancel-edit-btn').click(function() {
                let btn = $(this);
                let form = btn.closest('.card').find('form');
                let endpoint = form.data('endpoint');
                
                form[0].reset();
                form.find('input[name="id"]').val('');
                if (projectTechSelect) projectTechSelect.clear(); // Reset Tom Select
                form.find('.submit-btn').text('Add ' + endpoint.slice(0, -1).charAt(0).toUpperCase() + endpoint.slice(0, -1).slice(1));
                form.find('.submit-btn').removeClass('btn-warning').addClass('btn-success');
                btn.hide();
            });

            // Handle Delete
            $(document).on('click', '.delete-btn', function() {
                let btn = $(this);
                let endpoint = btn.data('endpoint');
                let id = btn.data('id');

                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to revert this!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Yes, delete it!'
                }).then((result) => {
                    if (result.isConfirmed) {
                        $.ajax({
                            url: `/api/${endpoint}/${id}/`,
                            type: 'DELETE',
                            success: function() {
                                loadList(endpoint, '#' + endpoint + '-list');
                                Swal.fire(
                                    'Deleted!',
                                    'Your file has been deleted.',
                                    'success'
                                )
                            }
                        });
                    }
                })
            });

        });