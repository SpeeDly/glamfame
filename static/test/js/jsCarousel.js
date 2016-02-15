$(document).ready(function() {  
        //move the last list item before the first item. The purpose of this is if the user clicks previous he will be able to see the last item.  
        $('#artists_container li:first').before($('#artists_container li:last'));
  
        //when user clicks the image for sliding right  
        $('.nav.next.clickable').click(function(){  
  
            //get the width of the items ( i like making the jquery part dynamic, so if you change the width in the css you won't have o change it here too ) '  
            var item_width = $('#artists_container li').outerWidth() + 10;  
  
            //calculate the new left indent of the unordered list  
            var left_indent = parseInt($('#artists_container').css('left')) - item_width;  
  
            //make the sliding effect using jquery's anumate function '  
            $('#artists_container').animate({'left' : left_indent},{queue:false, duration:500},function(){  
  
                //get the first list item and put it after the last list item (that's how the infinite effects is made) '  
                $('#artists_container li:last').after($('#artists_container li:first'));  
  
                //and get the left indent to the default -210px  
                $('#artists_container').css({'left' : '-210px'});  
            });  
        });  
  
        //when user clicks the image for sliding left  
        $('.nav.prev.clickable').click(function(){  
  
            var item_width = $('#artists_container li').outerWidth() + 10;  
  
            /* same as for sliding right except that it's current left indent + the item width (for the sliding right it's - item_width) */  
            var left_indent = parseInt($('#artists_container').css('left')) + item_width;  
  
            $('#artists_container').animate({'left' : left_indent},{queue:false, duration:500},function(){  
  
            /* when sliding to left we are moving the last item before the first item */  
            $('#artists_container li:first').before($('#artists_container li:last'));  
  
            /* and again, when we make that change we are setting the left indent of our unordered list to the default -210px */  
            $('#artists_container').css({'left' : '-210px'});  
            });  
  
        });  
  });