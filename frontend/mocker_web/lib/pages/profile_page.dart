import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:provider/provider.dart';
import '../models/user.dart';
import '../services/user_service.dart';
import '../services/auth_service.dart';
import '../widgets/navbar.dart';
import '../theme/app_theme.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final UserService _userService = UserService();
  final AuthService _authService = AuthService();
  User? _user;
  bool _loading = true;
  bool _isEditing = false;
  bool _saving = false;
  String? _error;

  // Form controllers
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _linkedinController = TextEditingController();
  final TextEditingController _githubController = TextEditingController();
  final TextEditingController _portfolioController = TextEditingController();
  final TextEditingController _additionalInfoController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadUserProfile();
    
    // listen to UserService changes
    _userService.addListener(_onUserServiceChanged);
  }

  @override
  void dispose() {
    _userService.removeListener(_onUserServiceChanged);
    _nameController.dispose();
    _emailController.dispose();
    _linkedinController.dispose();
    _githubController.dispose();
    _portfolioController.dispose();
    _additionalInfoController.dispose();
    super.dispose();
  }

  void _onUserServiceChanged() {
    if (_userService.currentUser != null && !_isEditing) {
      setState(() {
        _user = _userService.currentUser;
      });
      _populateFormControllers();
    }
  }

  Future<void> _loadUserProfile() async {
    try {
      setState(() {
        _loading = true;
        _error = null;
      });
      
      // check if user is logged in
      final authService = Provider.of<AuthService>(context, listen: false);
      final userId = authService.getUserId();
      
      if (userId == null) {
        throw Exception('User not authenticated');
      }
      
      // call service to get user profile
      final profile = await _userService.getUserProfile();
      setState(() {
        _user = profile;
        _loading = false;
      });
      
      // populate form controllers
      _populateFormControllers();
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  void _populateFormControllers() {
    if (_user != null) {
      _nameController.text = _user!.name;
      _emailController.text = _user!.email;
      _linkedinController.text = _user!.linkedinLink ?? '';
      _githubController.text = _user!.githubLink ?? '';
      _portfolioController.text = _user!.portfolioLink ?? '';
      _additionalInfoController.text = _user!.additionalInfo ?? '';
    }
  }

  Future<void> _pickAndUploadAvatar() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        setState(() => _saving = true);
        
        final file = result.files.first;
        
        final authService = Provider.of<AuthService>(context, listen: false);
        final userId = authService.getUserId();
        
        if (userId == null) {
          throw Exception('User not authenticated');
        }
        
        // call service to upload avatar (not pass userId, service internal parse from token)
        final avatarUrl = await _userService.uploadAvatar(file.path!);
        
        setState(() {
          _user = _user!.copyWith(photoURL: avatarUrl);
          _saving = false;
        });
        
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Avatar updated successfully'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to upload avatar: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _saveProfile() async {
    if (!_formKey.currentState!.validate()) return;

    try {
      setState(() => _saving = true);

      // check if user is logged in 
      final authService = Provider.of<AuthService>(context, listen: false);
      final userId = authService.getUserId();
      
      if (userId == null) {
        throw Exception('User not authenticated');
      }

      final updatedData = {
        'name': _nameController.text.trim(),
        'email': _emailController.text.trim(),
        'linkedinLink': _linkedinController.text.trim().isEmpty ? null : _linkedinController.text.trim(),
        'githubLink': _githubController.text.trim().isEmpty ? null : _githubController.text.trim(),
        'portfolioLink': _portfolioController.text.trim().isEmpty ? null : _portfolioController.text.trim(),
        'additionalInfo': _additionalInfoController.text.trim().isEmpty ? null : _additionalInfoController.text.trim(),
      };

      // call service to update user profile 
      final updatedUser = await _userService.updateUserProfile(updatedData);
      
      setState(() {
        _user = updatedUser;
        _isEditing = false;
        _saving = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Profile updated successfully'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      setState(() => _saving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Failed to update profile: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _toggleEditMode() {
    setState(() {
      _isEditing = !_isEditing;
      if (_isEditing) {
        _populateFormControllers();
      }
    });
  }

  void _cancelEdit() {
    setState(() {
      _isEditing = false;
    });
    _populateFormControllers(); // Reset form data
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text('Error: $_error', style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadUserProfile,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (_user == null) {
      return const Center(child: Text('No user data available'));
    }

    return Container(
      color: AppTheme.lightGray,
      child: Column(
        children: [
          // NavBar
          NavBar(
            title: 'Profile',
          ),
          
          // Main content
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 64.0, vertical: 32.0),
              child: Center(
                child: Container(
                  constraints: const BoxConstraints(maxWidth: 1200),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Edit Profile button in top left corner (only in view mode)
                      if (!_isEditing) ...[
                        Align(
                          alignment: Alignment.centerLeft,
                          child: ElevatedButton.icon(
                            onPressed: _toggleEditMode,
                            icon: const Icon(Icons.edit, size: 18),
                            label: const Text('Edit Profile'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.darkGray,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                              elevation: 2,
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                      ],
                      
                      // Profile content
                      _isEditing ? _buildEditForm() : _buildViewMode(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildViewMode() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        IntrinsicHeight( 
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Expanded(
                flex: 1,
                child: _buildInfoCard(
                  title: 'Basic Information',
                  children: [
                    Center( 
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 20,
                                  offset: const Offset(0, 6),
                                ),
                              ],
                            ),
                            child: CircleAvatar(
                              radius: 40, 
                              backgroundColor: const Color(0xFFE6CFE6), 
                              child: _user!.photoURL != null && _user!.photoURL!.isNotEmpty
                                  ? ClipOval(
                                      child: Image.network(
                                        _user!.photoURL!,
                                        width: 80,
                                        height: 80,
                                        fit: BoxFit.cover,
                                        errorBuilder: (context, error, stackTrace) {
                                          return const Icon(Icons.person, color: Color(0xFF263238), size: 40);
                                        },
                                      ),
                                    )
                                  : const Icon(Icons.person, color: Color(0xFF263238), size: 40),
                            ),
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // Name (centered)
                          Text(
                            _user!.name,
                            style: const TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF263238),
                              height: 1.2,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          
                          const SizedBox(height: 8),
                          
                          // Email (centered)
                          Text(
                            _user!.email,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                              fontWeight: FontWeight.w500,
                            ),
                            textAlign: TextAlign.center,
                          ),
                          
                          const SizedBox(height: 16),
                          
                          // Status badge (centered)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            decoration: BoxDecoration(
                              color: const Color(0xFF263238).withOpacity(0.1),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              'Active User',
                              style: TextStyle(
                                fontSize: 14,
                                color: const Color(0xFF263238),
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(width: 32),
              
              Expanded(
                flex: 2,
                child: _buildInfoCard(
                  title: 'Social Links',
                  children: [
                    if (_user!.linkedinLink != null && _user!.linkedinLink!.isNotEmpty) ...[
                      const SizedBox(height: 8), 
                      _buildInfoItem(
                        icon: Icons.work,
                        label: 'LinkedIn',
                        value: _user!.linkedinLink!,
                        isLink: true,
                      ),
                    ],
                    if (_user!.githubLink != null && _user!.githubLink!.isNotEmpty)
                      _buildInfoItem(
                        icon: Icons.code,
                        label: 'GitHub',
                        value: _user!.githubLink!,
                        isLink: true,
                      ),
                    if (_user!.portfolioLink != null && _user!.portfolioLink!.isNotEmpty)
                      _buildInfoItem(
                        icon: Icons.web,
                        label: 'Portfolio',
                        value: _user!.portfolioLink!,
                        isLink: true,
                      ),
                    if ((_user!.linkedinLink == null || _user!.linkedinLink!.isEmpty) &&
                        (_user!.githubLink == null || _user!.githubLink!.isEmpty) &&
                        (_user!.portfolioLink == null || _user!.portfolioLink!.isEmpty))
                      Container(
                        padding: const EdgeInsets.all(24),
                        child: Text(
                          'No social links added yet',
                          style: TextStyle(
                            color: Colors.grey[500],
                            fontSize: 14,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
        
        // Additional info section
        if (_user!.additionalInfo != null && _user!.additionalInfo!.isNotEmpty) ...[
          const SizedBox(height: 32),
          _buildInfoCard(
            title: 'Additional Information',
            children: [
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.grey[200]!),
                ),
                child: Text(
                  _user!.additionalInfo!,
                  style: const TextStyle(
                    fontSize: 15,
                    height: 1.6,
                    color: Color(0xFF263238),
                  ),
                ),
              ),
            ],
          ),
        ],
        
        // Sign Out button
        const SizedBox(height: 40),
        Center(
          child: SizedBox(
            width: 160,
            child: Consumer<AuthService>(
              builder: (context, authService, child) {
                return TextButton.icon(
                  onPressed: () async {
                    await authService.signOut();
                  },
                  icon: const Icon(Icons.logout, color: Colors.white, size: 20),
                  label: const Text(
                    'Sign Out',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
                    backgroundColor: const Color(0xFF263238),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(color: const Color(0xFF263238).withOpacity(0.3)),
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInfoCard({required String title, required List<Widget> children}) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 12,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(28.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
                color: Color(0xFF263238),
              ),
            ),
            const SizedBox(height: 24),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoItem({
    required IconData icon,
    required String label,
    required String value,
    bool isLink = false,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20, left: 16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF263238).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, size: 24, color: const Color(0xFF263238)),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 2),
                SelectableText(
                  value,
                  style: TextStyle(
                    fontSize: 14,
                    color: isLink ? const Color(0xFF263238) : Colors.black87,
                    decoration: isLink ? TextDecoration.underline : null,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEditForm() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.grey[200]!),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(48.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Editable avatar section
              _buildEditableAvatarSection(),
              const SizedBox(height: 48),
              
              // Form fields in a grid layout
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Left column
                  Expanded(
                    child: Column(
                      children: [
                        _buildFormField(
                          controller: _nameController,
                          label: 'Full Name',
                          icon: Icons.person,
                          validator: (value) => value?.isEmpty == true ? 'Name is required' : null,
                        ),
                        const SizedBox(height: 20),
                        _buildFormField(
                          controller: _emailController,
                          label: 'Email',
                          icon: Icons.email,
                          validator: (value) {
                            if (value?.isEmpty == true) return 'Email is required';
                            if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value!)) {
                              return 'Please enter a valid email';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 20),
                        _buildFormField(
                          controller: _linkedinController,
                          label: 'LinkedIn URL',
                          icon: Icons.work,
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(width: 32),
                  
                  // Right column
                  Expanded(
                    child: Column(
                      children: [
                        _buildFormField(
                          controller: _githubController,
                          label: 'GitHub URL',
                          icon: Icons.code,
                        ),
                        const SizedBox(height: 20),
                        _buildFormField(
                          controller: _portfolioController,
                          label: 'Portfolio URL',
                          icon: Icons.web,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 20),
              
              // Additional info field (full width)
              _buildFormField(
                controller: _additionalInfoController,
                label: 'Additional Information',
                icon: Icons.info,
                maxLines: 4,
              ),
              
              const SizedBox(height: 40),
              
              // Action buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  TextButton(
                    onPressed: _saving ? null : _cancelEdit,
                    style: TextButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                    ),
                    child: const Text(
                      'Cancel',
                      style: TextStyle(
                        fontSize: 16,
                        color: Color(0xFF263238),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),
                  ElevatedButton(
                    onPressed: _saving ? null : _saveProfile,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.darkGray,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                      elevation: 2,
                    ),
                    child: _saving
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text(
                            'Save Changes',
                            style: TextStyle(fontSize: 16),
                          ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEditableAvatarSection() {
    return Row(
      children: [
        // Avatar with edit button (smaller size)
        Stack(
          children: [
            Container(
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, 6),
                  ),
                ],
              ),
              child: CircleAvatar(
                radius: 40, 
                backgroundColor: const Color(0xFFE6CFE6), 
                child: _user!.photoURL != null && _user!.photoURL!.isNotEmpty
                    ? ClipOval(
                        child: Image.network(
                          _user!.photoURL!,
                          width: 80,
                          height: 80,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) {
                            return const Icon(Icons.person, color: Color(0xFF263238), size: 40);
                          },
                        ),
                      )
                    : const Icon(Icons.person, color: Color(0xFF263238), size: 40),
              ),
            ),
            Positioned(
              bottom: 6,
              right: 6,
              child: Container(
                decoration: BoxDecoration(
                  color: const Color(0xFF263238),
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: IconButton(
                  onPressed: _saving ? null : _pickAndUploadAvatar,
                  icon: _saving
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.camera_alt, color: Colors.white, size: 20),
                  padding: const EdgeInsets.all(10),
                ),
              ),
            ),
          ],
        ),
        
        const SizedBox(width: 32),
        
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Edit Profile',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF263238),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Update your profile information and avatar',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info, color: Colors.blue[700], size: 20),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Click the camera icon to change your avatar',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.blue[700],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFormField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    String? Function(String?)? validator,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      validator: validator,
      maxLines: maxLines,
      style: const TextStyle(
        fontSize: 16,
        color: Color(0xFF263238),
      ),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(
          fontSize: 16,
          color: Colors.grey[600],
          fontWeight: FontWeight.w500,
        ),
        prefixIcon: Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF263238).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: const Color(0xFF263238), size: 20),
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Color(0xFF263238), width: 2),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Colors.red, width: 1),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: Colors.red, width: 2),
        ),
        filled: true,
        fillColor: Colors.grey[50],
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        floatingLabelBehavior: FloatingLabelBehavior.auto,
      ),
    );
  }
} 