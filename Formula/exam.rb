class Exam < Formula
	include Language::Python::Virtualenv
	desc "An open source tool for generating exams"
	homepage "https://www.razer.net.br/exam"
	url "https://bitbucket.org/user/repo/get/HEAD.zip", :using => :curl
  
	depends_on "python@3.8"
  
	resource "aiofiles" do
	  url "https://files.pythonhosted.org/packages/2b/64/437053d6a4ba3b3eea1044131a25b458489320cb9609e19ac17261e4dc9b/aiofiles-0.5.0.tar.gz"
	  sha256 "98e6bcfd1b50f97db4980e182ddd509b7cc35909e903a8fe50d8849e02d815af"
	end
  
	# ... many more resource blocks ...
  
	def install
	  virtualenv_install_with_resources
	end
  
	test do
	  system bin/"datasette", "--help"
	end
  end